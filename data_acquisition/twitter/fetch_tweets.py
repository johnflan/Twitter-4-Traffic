"""
Module for harvesting tweets from twitter search api.
Typical calling command:
$ python uktwaffic -t 'traffic OR accident OR tailback OR gridlock OR m25 OR standstill OR road OR street OR stuck OR car OR bus OR train' database_file.sqlite 
## if you only want tweets with an id higher than MINID then use this (better search terms too)
$ python uktwaffic -i ${MINID} -t 'traffic OR accident OR tailback OR gridlock OR m25 OR standstill OR road OR street OR stuck OR car OR bus OR train OR signals OR incident -web -google -marketing' database_file.sqlite 
"""
import os
import sys
import re
import pg8000
from pg8000 import DBAPI 
from pg8000.errors import ProgrammingError
import ConfigParser
import twitter
from twitter import TwitterError
from urllib2 import URLError
import time
from datetime import datetime
DATETIME_STRING_FORMAT = '%a, %d %b %Y %H:%M:%S +0000'
DATETIME_STAMP_STRING_FORMAT = '%Y%m%d%H%M%S'
from logging import FATAL, ERROR, WARNING, INFO, DEBUG
import pickle
from classifier_files.preprocessor import preprocessor


if __name__ == '__main__':
    import sys
    sys.path.append('..')

from crawler import GetRateLimiter, SuppressedCallException

def tweets(  conn,
                rl,
                georadius="19.622mi",
                start_id=0,
                **kwargs):
    term = kwargs['terms']
    cursor = conn.cursor()
    most_recent_id = start_id
    geocount = 0
    retweetRegex = re.compile('/\brt\b/i')
    
    #>>>>>>>>>>LOAD THE CLASSIFIER<<<<<<<<<<<<<
    classifier = pickle.load(open("naive_bayes.pickle"))
    
    while True:
        since_id = most_recent_id
        results = None
        page = 0
        print "Getting results since ", since_id
        while results != [] and page <= 15:
            page += 1
            try:
                print "Getting results page:", page
                print "georadius", georadius
                searchargs = dict(geocode=(51.5,-0.15,georadius),per_page=100,page=page,since_id=since_id,term=term)
                print "[twitter] rl.FreqLimitGetSearch - %r" % searchargs
                
                #GET RESULTS 
                results = rl.FreqLimitGetSearch(**searchargs)
                
                for r in results:
                    most_recent_id = max(r.id,most_recent_id)
                    (tid,uname,created_at_str,location,text,geo) = r.id,r.user.screen_name,r.created_at,r.location,r.text,r.GetGeo()
                    created_at = datetime.strptime(created_at_str, DATETIME_STRING_FORMAT)
					
                    text = text.encode('ascii','ignore')
                    
                    #>>>>>>>>>>>>>>>>>>CLASSIFY THE TWEET<<<<<<<<<<<<<<<<<<<<<<<
                    isTraffic, probability = classify_traffic(text,classifier)    

                    now = datetime.now()
                    nowstr = datetime.strftime(now, DATETIME_STRING_FORMAT)
                    #print (tid,uname,created_at,location,text,geo)

                    # If the tweet is a retweet drop it, this method is not
                    # 100%. But the API is not returning if r.retweet
                    isRetweet = re.search('RT\s@', r.text, re.IGNORECASE)
                    if isRetweet or not isTraffic:
                        continue
                    print "Found one"
                    # geo part
                    if not geo is None and geo.get('type') == 'Point':
                        geolat,geolong, = geo['coordinates']
                        geocount += 1
                        #print "\t### got one at: ", geo['coordinates'], "that makes %d" % geocount
                        geoloc = "ST_GeographyFromText('SRID=4326;POINT(" + str(geolong) + " " + str(geolat) + ")')"

                        text = text.replace("'", "")
                        text = text.replace("%", "")
                        query = "INSERT INTO tweets(tid, uname, created_at,\
                        location,text,geolocation,probability) VALUES (" + str(tid) +\
                        ",'" + uname + "', to_timestamp('" + str(created_at) + "','YYYY-MM-DD HH24:MI:SS'),'" +\
                        str(location) + "',\'" + str(text) +\
                        "\'," + geoloc + "," + str(probability) + ")"

                        print query
                        print uname, "\t", text[:50], geo['coordinates']
                        #query = """INSERT INTO tweets(tid, uname,
                        #created_at, location, text, geolocation)
                        #      VALUES(%s,%s,to_timestamp(%s, \'YYYY-MM-DD
                        #      HH24:MI:SS\'),%s,%s,ST_GeographyFromText(SRID=4326;POINT(%s,%s)))"""
                        #params = (tid,uname,str(created_at),location,text,str(geolong),str(geolat))
                        #print "[sql] params ", query
                        try:
                            cursor.execute( query )
                        except ProgrammingError, e:
                            print query
                            print e
                            continue

                    else:
                        sql_query = """INSERT INTO tweets(tid, uname, created_at, location, text, probability ) VALUES
                                    (%s,%s,to_timestamp(%s, \'YYYY-MM-DD HH24:MI:SS\'),%s,%s,%s)"""
                        params = (tid, uname, str(created_at), location, text, probability)
                        #print "[params]", params
                        print uname, "\t", text[:50]
                        try:
                            cursor.execute(sql_query, params)
                        except ProgrammingError, e:
                            print params
                            print e
                            continue
                    conn.commit()
            except TwitterError, e:
                print
                print "[ERROR] TwitterError: ", e, "page:",page, "since_id",since_id
                results = []
                print
            except URLError, e:
                print "[ERROR] URLError: ", e, "page:",page, "since_id",since_id
                results = []

def loadSearchTerms(kwargs):
    try:
        f = open("searchTerms.txt", "r")
        terms = f.read()
        print "[INFO] Search Terms: ", terms
        kwargs['terms'] = terms.strip()
    except IOError:
        print "[Error] search terms file not found"
        sys.exit()


def main(*args,**kwargs):
    configSection = "Local database"
    Config = ConfigParser.ConfigParser()
    Config.read("t4t_credentials.txt")
    cfg_username = Config.get(configSection, "username")
    cfg_password = Config.get(configSection, "password")
    cfg_database = Config.get(configSection, "database")
    cfg_server = Config.get(configSection, "server")

    if cfg_server == "" \
            or cfg_database == "" \
            or cfg_username == "" \
            or cfg_password == "":
        print "Could not load config file"
        sys.exit(0)

    if kwargs['verbosity'] <= DEBUG:
        print "[debug] main args", args
        print "[debug] main kwargs", kwargs
    
    conn = DBAPI.connect(host=cfg_server, database=cfg_database,
            user=cfg_username, password=cfg_password)
    cursor = conn.cursor()

    if kwargs['query_max_id']:
        print get_max_id(conn,cursor)
        return

    loadSearchTerms(kwargs)

    start_id = get_max_id(conn,cursor)
    print start_id
    if start_id is not None:
        kwargs['start_id'] = int(start_id)

    rl = GetRateLimiter()
    rl.api._cache_timeout = 30
    tweets(conn,rl,**kwargs)


def get_max_id(conn,cursor):
    query = 'SELECT MAX(tid) FROM geolondon'
    cursor.execute(query)
    ((start_id,),) = cursor.fetchall()
    return start_id
    
def classify_traffic(text,classifier):
    pro_text = preprocessor().preprocess(text,[])
    ft_pro_text = dict([(word, True) for word in pro_text])
    label = classifier.classify(ft_pro_text)
    isTraffic = False
    probability = 0
    #>>>>>>>>>>>>>>>>>>>>>FIND THE PROBABILITY<<<<<<<<<<<<<<<<<
    if label == 'traffic':
        isTraffic = True 
        probability_dict  = classifier.prob_classify(ft_pro_text)
        probability = probability_dict.prob('traffic')
		
	print text, probability, isTraffic
    return isTraffic, probability

if __name__ == '__main__':
    import StringIO
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-i',
                        dest='start_id',
                        type=int,
                        default=0,
                        help='Start id to scan from')
    parser.add_option('-r',
                        dest='georadius', 
                        default='20.0mi', 
                        help='The radius of the geocode entry')
    parser.add_option('-v', '--verbosity',
                        dest='verbosity', 
                        default=WARNING, 
                        type=int,
                        help='Set the verbosity')
    parser.add_option('-x', '--query-max-id',
                        dest='query_max_id', 
                        default=False, 
                        action ='store_true',
                        help='Simply return the maximum id currently in the table')    
    (options, args) = parser.parse_args()
    kwargs = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])
    main(*args,**kwargs)

