import os
import sys
import re
import pg8000
from pg8000 import DBAPI
import ConfigParser
import twitter
from twitter import TwitterError
from urllib2 import URLError
import time
from time import strftime
from datetime import datetime
DATETIME_STRING_FORMAT = '%a, %d %b %Y %H:%M:%S +0000'
DATETIME_STAMP_STRING_FORMAT = '%Y%m%d%H%M%S'
from logging import FATAL, ERROR, WARNING, INFO, DEBUG
import pickle
from classifier_files.preprocessor import preprocessor
from crawler import GetRateLimiter, SuppressedCallException
import StringIO
from optparse import OptionParser
import thread

def main():
    # Connect to the database
    connect()

    # Load the twitter search terms from a file
    loadSearchTerms()

    # Find the maximum tweet id that was previously stored in the database
    start_id = get_max_id()

    if start_id is not None:
        kwargs['start_id'] = int(start_id)

    rl = GetRateLimiter()
    rl.api._cache_timeout = 30
    tweets(rl, kwargs['georadius'], kwargs['start_id'])

###############################################################################################
############################ Creates a connection to the db ###################################
###############################################################################################

def connect():
    global conn
    global cursor
    try:
        # Create a connection to the database
        conn = DBAPI.connect(**db)
        # Create a cursor that will be used to execute queries
        cursor = conn.cursor()
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # Exit the script/thread and print an error telling what happened.
        print "Database connection failed! -> %s" % (exceptionValue)
        sys.exit()

###############################################################################################
######################## Loads the twitter search terms from a file ###########################
###############################################################################################
        
def loadSearchTerms():
    try:
        f = open(kwargs['terms'], "r")
        terms = f.read()
        print "[INFO] Search Terms: %s" % terms
        kwargs['terms'] = terms.strip()
    except IOError:
        print "[Error] search terms file not found"
        sys.exit()

###############################################################################################
############### Finds the maximum id that is already stored in the database ###################
###############################################################################################
        
def get_max_id():
    query = 'SELECT MAX(tid) FROM tweets'
    cursor.execute(query)
    ((start_id,),) = cursor.fetchall()
    return start_id

###############################################################################################
########################## Store the traffic tweets in the database ###########################
###############################################################################################
    
def tweets(rl, georadius="19.622mi", start_id=0):
    term = kwargs['terms']
    cursor = conn.cursor()
    most_recent_id = start_id

    retweetRegex = re.compile('/\brt\b/i')
    
    # Load the classifier
    classifier = pickle.load(open(kwargs['classifier']))

    while True:
        # Metrics for the tweets
        total_tweets = 0
        traffic_tweets = 0
        rightturn_tweets = 0
        retweets = 0
        geotweets = 0

        # Get the current time
        updated_at = strftime("%d/%m/%y %H:%M:%S")
        
        since_id = most_recent_id
        results = None
        page = 0
        hashtagRT = '#RightTurn'
        while results != [] and page <= 15:
            page += 1
            try:
                results = None
                searchargs = dict(geocode=(51.5,-0.15,georadius),per_page=100,page=page,since_id=since_id,term=term)
                
                # Get results from twitter
                results = rl.FreqLimitGetSearch(**searchargs)
		total_tweets += len(results)

                for r in results:
                    most_recent_id = max(r.id,most_recent_id)
                    (tid,uname,rname,created_at_str,location,text,geo) = r.id,r.user.screen_name,r.user.name,r.created_at,r.location,r.text,r.GetGeo()
                    created_at = datetime.strptime(created_at_str, DATETIME_STRING_FORMAT)
                    
                    rname = rname.encode('ascii','ignore')
                    text = text.encode('ascii','ignore')
                    probability = 1.0
                    isTraffic = True
                    isRetweet = False
                    
                    # Find if it is a retweet
                    if hashtagRT not in text: 
                        # Classify the tweet
                        isTraffic, probability = classify_traffic(text,classifier)    

                        # If the tweet is a retweet drop it, this method is not
                        # 100%. But the API is not returning if r.retweet
                        isRetweet = re.search('RT\s@', r.text, re.IGNORECASE)
                    else:
                        rightturn_tweets += 1

                    # Do not use the tweet if one of these conditions is true
                    if not isTraffic or probability < 0.98:
                        continue
                    elif isRetweet:
                        retweets += 1
                        continue
                    
                    traffic_tweets += 1
    
                    # If the tweet has geolocation
                    if not geo is None and geo.get('type') == 'Point':
                        geolat,geolong, = geo['coordinates']
                        geotweets += 1
                        
                        geoloc = "ST_GeographyFromText('SRID=4326;POINT(" + str(geolong) + " " + str(geolat) + ")')"

                        text = text.replace("'", "")
                        text = text.replace("%", "")
                        query = "INSERT INTO tweets(tid, uname, rname, created_at,\
                        location,text,geolocation,probability) VALUES (" + str(tid) +\
                        ",'" + uname + "','" + rname + "', to_timestamp('" + str(created_at) + "','YYYY-MM-DD HH24:MI:SS'),'" +\
                        str(location) + "',\'" + str(text) +\
                        "\'," + geoloc + "," + str(probability) + ")"
                        
                        try:
                            cursor.execute( query )
                        except:
                            # Get the most recent exception
                            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                            print "Error -> %s, tid = %s" % (exceptionValue,tid)
                            continue
                    
                    # If the tweet does not have geolocation
                    else:
                        query = """INSERT INTO tweets(tid, uname, rname, created_at, location, text, probability ) VALUES
                                    (%s,%s,%s,to_timestamp(%s, \'YYYY-MM-DD HH24:MI:SS\'),%s,%s,%s)"""
                        params = (tid, uname, rname, str(created_at), location, text, probability)
                        
                        try:
                            cursor.execute(query, params)
                        except:
                            # Get the most recent exception
                            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                            print "Error -> %s, tid = %s" % (exceptionValue,tid)
                            continue
                    # Commit the changes to the database
                    conn.commit()
                print "Tweets Stored until tid %s @%s" % (most_recent_id,updated_at)
            except TwitterError, e:
                print "[ERROR] TwitterError: ", e, "page:",page, "since_id",since_id
                results = []
            except URLError, e:
                print "[ERROR] URLError: ", e, "page:",page, "since_id",since_id
                results = []
        try:
            # Delete old tweets from the table
            query = """DELETE FROM tweets WHERE created_at < current_timestamp - interval '36' hour"""
            cursor.execute(query)
            
            # Update tweet metrics
            query = """UPDATE tweets_metrics SET total_tweets=total_tweets+%s,
                                                 traffic_tweets=traffic_tweets+%s,
                                                 rightturn_tweets=rightturn_tweets+%s,
                                                 retweets=retweets+%s,
                                                 geotweets=geotweets+%s""" % (str(total_tweets),str(traffic_tweets),str(rightturn_tweets),str(retweets),str(geotweets))
            cursor.execute(query)
            # Commit the changes to the database
            conn.commit()
        except:
            # Get the most recent exception
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print "Error -> %s" % (exceptionValue)

###############################################################################################
########################## Classify a tweet to traffic or not traffic #########################
###############################################################################################

def classify_traffic(text,classifier):
    pro_text = preprocessor().preprocess(text,[])
    ft_pro_text = dict([(word, True) for word in pro_text])
    label = classifier.classify(ft_pro_text)
    isTraffic = False
    probability = 0
    
    # Find the probability
    if label == 'traffic':
        isTraffic = True 
        probability_dict  = classifier.prob_classify(ft_pro_text)
        probability = probability_dict.prob('traffic')
        
    return isTraffic, probability

###############################################################################################
######################### Executed if the script is run directly ##############################
###############################################################################################
    
if __name__ == '__main__':
    # Read the database values from a file
    Config = ConfigParser.ConfigParser()
    Config.read("../../t4t_credentials.txt")
    
    configSection = "Local database"
    db = dict()
    db['user'] = Config.get(configSection, "username")
    db['password'] = Config.get(configSection, "password")
    db['database'] = Config.get(configSection, "database")
    db['host'] = Config.get(configSection, "server")

    # Parse the command line arguments
    parser = OptionParser()
    parser.add_option('-g', '--georadius',
                        dest='georadius', 
                        default='20.0mi', 
                        help='The radius of the geocode entry')
    parser.add_option('-t', '--terms',
                        dest='terms',
                        default='searchTerms.txt',
                        help='The search terms for twitter')
    parser.add_option('-c', '--classifier',
                        dest='classifier',
                        default='naive_bayes.pickle',
                        help='The classifier file')
    parser.add_option('-v', '--verbosity',
                        dest='verbosity', 
                        default=WARNING, 
                        type=int,
                        help='Set the verbosity')
    (options, args) = parser.parse_args()
    kwargs = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])
    
    main()

###############################################################################################
############################ Executed if the script is imported ###############################
###############################################################################################

else:
    db = dict()
    kwargs = dict()

def startThread():
    # Create a new thread
    thread.start_new_thread(main, ())
