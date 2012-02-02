#! /usr/bin/env python
 
import tweetstream
import ConfigParser
import pg8000
from pg8000 import DBAPI

username = "t4traffic"
password = "uktwaffic"
words = ["traffic", "accident", "tailback", "gridlock", "m25", "standstill", "road", "street", "stuck", "car", "bus", "train"]
follow = ""
locations = ["51.25,-0.598", "51.75,0.372"]

configSection = "Local database"
Config = ConfigParser.ConfigParser()
Config.read("../t4t_credentials.txt")
cfg_username = Config.get(configSection, "username")
cfg_password = Config.get(configSection, "password")
cfg_database = Config.get(configSection, "database")
cfg_server = Config.get(configSection, "server")

conn = DBAPI.connect(host=cfg_server, database=cfg_database,user=cfg_username, password=cfg_password)
cursor = conn.cursor()

#create_query = """CREATE TABLE tweet_stream(tid BIGINT PRIMARY KEY,uname
#VARCHAR(40), created_at TIMESTAMP,location VARCHAR(128), text VARCHAR(200), geolat
#    FLOAT, geolong FLOAT )"""
#cursor.execute(create_query)
#conn.commit()

searchTermsFile = open("searchTerms.txt", "r")
searchTerms = []
for line in searchTermsFile:
    searchTerms.append(line.strip())

print searchTerms,locations 
#stream = tweetstream.FilterStream(username, password, locations=locations, track=searchTerms) 
stream = tweetstream.FilterStream(username, password, locations=locations)

try:
    for tweet in stream:
        if tweet.has_key('retweeted'):
            retweeted = tweet['retweeted']
        if tweet.has_key("text") and not retweeted: 
            text = tweet['text'].encode('ascii','ignore')
            uname = tweet['user']['screen_name'].encode('ascii','ignore')
            #storeTweet(tweet)
            #print uname, "--", text
            if tweet['user'].has_key('location'):
                location = tweet['user']['location']
                if not location == None: 
                    location = location.encode('ascii','ignore')
                    print location
except tweetstream.ConnectionError, e:
    print "Disconnected from twitter. Reason:", e.reason

def storeTweet(tweet):
    #print tweet['user']['screen_name'] + ": " + tweet['text']
	#print "Coord:", tweet['coordinates'], tweet['place'], tweet['geo'], "\n"
    print tweet
