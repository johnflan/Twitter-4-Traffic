import os
import sys
import re
import pg8000
from pg8000 import DBAPI
import ConfigParser
import soundex.returnsoundex

def main():
    # Connect to the database
    connect()

    # Create the object for the class returnsoundex
    sdx = soundex.returnsoundex.returnsoundex()
    cursor = conn.cursor()
    # Update tweet metrics
    query = "UPDATE geolooukup SET soundex =" + sdx.soundexstring( + "soundex"+ )""
    cursor.execute(query)
    # Commit the changes to the database
    conn.commit()
			
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
