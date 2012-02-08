#! /usr/bin/env python

from pg8000 import DBAPI
import sys
import optparse



def main(action, *args, **db):
    if action=="showTweets":
            showTweets(db)


def showTweets(**db):
    try:
        conn = DBAPI.connect(**db)
        cursor = conn.cursor()
        cursor.execute("""SELECT * from labelled_tweets""")
        rows = cursor.fetchall()
        print "connected"
        for row in rows:
	        print row
    except:
	    print "Unable to connect to the database"

if __name__ == "__main__":
    configSection = "Local database"
    Config = ConfigParser.ConfigParser()
    Config.read("t4t_credentials.txt")
    user = Config.get(configSection, "username")
    password = Config.get(configSection, "password")
    database = Config.get(configSection, "database")
    host = Config.get(configSection, "server")



