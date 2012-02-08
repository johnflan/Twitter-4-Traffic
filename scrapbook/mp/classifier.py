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

	# Parse options from the command line
	parser = optparse.OptionParser("usage: %prog [options] [action] [tables]")
	parser.add_option('-H','--host',
					dest='host',
					default=host,
					help='The hostname of the DB')
	parser.add_option('-d','--database',
					dest='database',
					default=database,
					help='The name of the DB')
	parser.add_option('-U','--user',
					dest='user',
					default=user,
					help='The username for the DB')
	parser.add_option('-p','--password',
					dest='password',
					default=password,
					help='The password for the DB')

	(options, args) = parser.parse_args()

	db = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])
	# Needs an argument (setup, remove or drop)
	if len(args)==0:
		sys.exit("Wrong number of arguments")

	sys.exit(main(args[0], *args, **db))