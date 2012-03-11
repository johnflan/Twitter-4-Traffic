import os
import sys
import re
import pg8000
from pg8000 import DBAPI
import ConfigParser
import twitter
from twitter import TwitterError
import urllib
import urllib2
from urllib2 import URLError
import time
from time import strftime
from datetime import datetime
DATETIME_STRING_FORMAT = '%a, %d %b %Y %H:%M:%S +0000'
DATETIME_STAMP_STRING_FORMAT = '%Y%m%d%H%M%S'
from logging import FATAL, ERROR, WARNING, INFO, DEBUG
import pickle
from classifier_files.preprocessor import preprocessor
import soundex.returnsoundex
from crawler import GetRateLimiter, SuppressedCallException
import StringIO
from string import punctuation
from operator import itemgetter
from googlemaps import GoogleMaps
from optparse import OptionParser
import thread
import json
from json import JSONDecoder

addressRegex = r"(\b(in|at|on|\w,)\s((\d+|\w{2,})\s){1,3}(st(reet)?|r[(oa)]d|bridge|ave(nue)?|park){1,2}(\sstation|\smarket)?[,.\s\z$]{1})" 

GEOCODE_BASE_URL = "http://maps.googleapis.com/maps/api/geocode/json"

###############################################################################################
############################ Start the twitter collection feed ################################
###############################################################################################

def main():
    # Connect to the database
    connect()

    # Load the twitter search terms from a file
    loadSearchTerms()
    
    # Load the profanity filter words from a file
    loadBadWords()

    # Update the database's bad words in tweets
    updateDBBadWords()
    
    # Load the twitter user blacklist from a file
    loadBlacklist()
    
    # Remove from the database previously posted tweets from blacklisted users
    updateDBBlacklist()
    
    # Find the maximum tweet id that was previously stored in the database
    start_id = get_max_id()

    if start_id is not None:
        kwargs['start_id'] = int(start_id)
    else:
        kwargs['start_id'] = 0

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
        kwargs['terms'] = terms.strip()
    except IOError:
        print "[Error] search terms file not found"
        sys.exit()
        
###############################################################################################
############################# Loads bad words list from a file ################################
###############################################################################################
        
def loadBadWords():
    try:
        f = open(kwargs['badwords'], "r")
        badwords = f.read()
        # Add all words but remove the last new line
        kwargs['badwords'] = badwords.split("\n")[:-1]
    except IOError:
        print "[Error] bad words file not found"
        sys.exit()
        
###############################################################################################
######################## Loads the twitter user blacklist from a file #########################
###############################################################################################
        
def loadBlacklist():
    try:
        f = open(kwargs['blacklist'], "r")
        blacklist = f.read()
        kwargs['blacklist'] = blacklist.split("\n")[:-1]
    except IOError:
        print "[Error] blacklist file not found"
        sys.exit()

###############################################################################################
####################### Update the tweets column for the new bad words ########################
###############################################################################################
        
def updateDBBadWords():
    try:
        query = "UPDATE tweets SET profanity='n'"
        
        cursor.execute(query)
        
        query = "UPDATE tweets SET profanity='y' WHERE "
        
        for word in kwargs['badwords']:
            if word!=None and len(word)>0:
                query += "text ~* '[[:<:]]" + word + "[[:>:]]' OR "
        
        if len(kwargs['badwords'][0]) > 0:
            cursor.execute(query[:-4])
            conn.commit()
    except IOError:
        print "[Error] bad words could not be updated"
        sys.exit()
        
###############################################################################################
####################### Update the tweets column for the new bad words ########################
###############################################################################################
        
def updateDBBlacklist():
    try:
        query = "DELETE FROM tweets WHERE "
        
        for user in kwargs['blacklist']:
            if user!=None and len(user)>0:
                query += "uname='" + user + "' OR "
        
        if len(kwargs['blacklist'][0]) > 0:
            cursor.execute(query[:-4])
            conn.commit()
    except IOError:
        print "[Error] blacklist could not be updated"
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
    
    # Create the object for the class returnsoundex
    sdx = soundex.returnsoundex.returnSoundex()

    while True:
        # Metrics for the tweets
        total_tweets = 0
        traffic_tweets = 0
        rightturn_tweets = 0
        retweets = 0
        geotweets = 0
        foundgeotweets = 0

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
                    
                    # If the user is blacklisted do not store the tweet
                    if uname in kwargs['blacklist']:
                        continue
                    
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

                    # If the tweet does not have geolocation
                    if geo is None:
                        print "IT DOESNT HAVE GEOLOCATION"
                        geolat, geolong = findGeolocation(text,sdx)
                        if geolat!=None and geolong!=None:
                            foundgeotweets += 1
                    elif not geo is None and geo.get('type') == 'Point':
                        print "IT HAS GEOLOCATION"
                        geolat, geolong = geo['coordinates']
                    else:
                        continue
                        
                    # Profanity checking
                    profanity = "n"
                    for word in kwargs['badwords']:
                        # The pattern is the word without no letters or numbers befere and after it
                        pattern = '(\W|\Z)%s(\W|\Z)' % word
                        result = re.search(pattern, text, flags=re.IGNORECASE)
                        
                        if result!=None:
                            profanity = "y"
                            break

                    # If the tweet has geolocation
                    if geolat!=None and geolong!=None:
                        geotweets += 1
                        
                        geoloc = "ST_GeographyFromText('SRID=4326;POINT(" + str(geolong) + " " + str(geolat) + ")')"

                        text = text.replace("'", "")
                        text = text.replace("%", "")
                        query = "INSERT INTO tweets(tid, uname, rname, created_at,\
                        location,text,geolocation,probability,profanity) VALUES (" + str(tid) +\
                        ",'" + uname + "','" + rname + "', to_timestamp('" + str(created_at) + "','YYYY-MM-DD HH24:MI:SS'),'" +\
                        str(location) + "',\'" + str(text) +\
                        "\'," + geoloc + "," + str(probability) + ",'" + str(profanity) + "')"
                        
                        try:
                            cursor.execute( query )
                        except:
                            # Get the most recent exception
                            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                            print "Error -> %s, tid = %s" % (exceptionValue,tid)
                            continue
                    
                    # If the tweet does not have geolocation
                    else:
                        query = """INSERT INTO tweets(tid, uname, rname, created_at, location, text, probability, profanity ) VALUES
                                    (%s,%s,%s,to_timestamp(%s, \'YYYY-MM-DD HH24:MI:SS\'),%s,%s,%s,%s)"""
                        params = (tid, uname, rname, str(created_at), location, text, probability, profanity)
                        
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
            query = """DELETE FROM tweets WHERE created_at < current_timestamp - interval '7' day"""
            cursor.execute(query)
            
            # Update tweet metrics
            query = """UPDATE tweets_metrics SET total_tweets=total_tweets+%s,
                                                 traffic_tweets=traffic_tweets+%s,
                                                 rightturn_tweets=rightturn_tweets+%s,
                                                 retweets=retweets+%s,
                                                 geotweets=geotweets+%s,
                                                 foundgeotweets=foundgeotweets+%s""" % (str(total_tweets),str(traffic_tweets),str(rightturn_tweets),str(retweets),str(geotweets),str(foundgeotweets))
            cursor.execute(query)
            # Commit the changes to the database
            conn.commit()
        except:
            # Get the most recent exception
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print "Error -> %s" % (exceptionValue)

###############################################################################################
##################### Find the geolocation and update the geolookup table #####################
###############################################################################################

def findGeolocation(text,sdx):
    # Check if the tweet contains the regex
    regexMatch = re.search(addressRegex, text, re.IGNORECASE)
    print "BEFORE THE REGEX"
    if regexMatch != None:
        print "INSIDE THE REGEX - match regex"
        addr = regexMatch.group(0)[3:] 
        addr = addr.strip(punctuation).lower().strip()
        
        #CHANGE: Find the soundex for the address
        soundex = sdx.soundexstring(str(addr))
        
        if ("the street" in addr) or ("my street" in addr) or ("this street" in addr) or ("our street" in
            addr) or ("a street" in addr) or ("high street" in addr) or ("upper st" in addr) or ("car park" in addr) or ("the park" in addr) or ("in every" in addr):
            return (None, None)

        # Try to find the corresponding geolocation in the local table geolookup
        try:
            # CHANGE: Replcae addr with soundex
            # rows = get_db_geo(addr)
            latlon = get_db_geo(soundex)        
            latitude, longitude = latlon[6:-1].split()
            print "FOUND THE LATLON FROM THE TABLE : lat = %s and lon = %s" % (latitude, longitude)
            return (latitude, longitude)
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print "Error -> %s" % (exceptionValue)
            # There is no such an address in the geolookup table so go and try to add it
            try:
                latitude, longitude = geocode(address = addr+",london, UK", sensor = "false")
                geoloc = "ST_GeographyFromText('SRID=4326;POINT("+str(latitude)+" "+str(longitude)+")')"
                query = "INSERT INTO geolookup (streetaddress,latlon,soundex)VALUES('"+str(addr)+"',"+geoloc+",'"+soundex+"')"
                cursor.execute(query)
                print "FOUND THE LATLON FROM THE GOOGLEMPAS : lat = %S and lon = %s" % (latitude, longitude)
                return (latitude, longitude)
            except:
                exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                print "Error -> %s" % (exceptionValue)
                return (None, None)
    else:
        return(None, None)

###############################################################################################
######## Parse the json file from google map and get lat and lon for the address ##############
###############################################################################################

def geocode(address, sensor):
    geo_args = dict({"address":address,"sensor":sensor})
    
    url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
    req = urllib2.Request(url)
    result = urllib2.urlopen(req)
    response = result.read()

    decoder = json.JSONDecoder()
    jsonObj = decoder.decode(response)
    lat = jsonObj['results'][0]['geometry']['location']['lat']
    lng = jsonObj['results'][0]['geometry']['location']['lng']
    
    print "INSIDE GEOCODE : GOT the lat %s and lng %s from googlempas:" % (lat,lng)
    return (lat,lng)

###############################################################################################
###### Get the lon and lat from the geolookup and match them with the addr if it exists #######
###############################################################################################

def get_db_geo(soundex):
    # CHANGE : Select the lat and the lon from the geolookup if the soundex matches
    # query1 = "SELECT ST_AsText(latlon) as latlon FROM geolookup WHERE streetaddress ='"+str(addr)+"'"
    print "INSIDE get_db_geo : SOUNDEX : %s" % soundex
    query = "SELECT ST_AsText(latlon) as latlon FROM geolookup WHERE soundex ='"+str(soundex)+"'"
    cursor.execute(query)
    try:
        result = cursor.fetchone()
        print "FOUND latlot : %s" % result[0]
        return result[0]
    except:
        return None

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
    parser.add_option('-w', '--words',
                        dest='badwords',
                        default='dirty_words.txt',
                        help='The bad words for the profanity filter')
    parser.add_option('-b', '--blacklist',
                        dest='blacklist',
                        default='blacklist.txt',
                        help='The blacklist for twitter users')
    parser.add_option('-c', '--classifier',
                        dest='classifier',
                        default='/srv/t4t/classifier_files/naive_bayes.pickle',
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
