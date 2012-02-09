#! /usr/bin/env python

from pg8000 import DBAPI
import sys
import optparse
import ConfigParser


def main(action,*args, **db):

    connectDB(**db)

    if action=="train":
        trainClassifier(*args)

    elif action == "test":
        testClassifier(*args)

    elif action == "classify":
        classifyTweet(*args)

    else:
        print "\nPlease choose an action between train, test & classify\n"


def connectDB(**db):
    try:
        conn = DBAPI.connect(**db)
        cursor = conn.cursor()
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        sys.exit("Database connection failed! ->%s" % (exceptionValue))
    return cursor, conn


def trainClassifier(*args):
    print "todo train"


def testClassifier(*args):
    print "todo test"

def classifyTweet(*args):
    print "todo real classification finally"


if __name__ == "__main__":
    configSection = "Local database"
    Config = ConfigParser.ConfigParser()
    Config.read("t4t_credentials.txt")
    user = Config.get(configSection, "username")
    password = Config.get(configSection, "password")
    database = Config.get(configSection, "database")
    host = Config.get(configSection, "server")
    action = 'noAction'

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
    parser.add_option('-a','--action',
                    dest='action',
                    default=0,
                    help='The action the classifier will execute')
    (options, args) = parser.parse_args()
    
    db = dict([[k,v] for k,v in options.__dict__.iteritems() if not v is None ])

    sys.exit(main(*args, **db))
