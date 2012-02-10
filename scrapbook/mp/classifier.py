#! /usr/bin/env python

from pg8000 import DBAPI
import sys
import optparse
import ConfigParser
import nltk


features = []

def main(*args,**opts):
    db = dict([ ['host',opts['host']], ['database',opts['database']],
        ['user',opts['user']], ['password',opts['password']]])

    cursor,conn = connectDB(**db)
    
    action = opts['action']

    if action=="train":
        trainClassifier(conn, cursor, opts['tablename'])

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


def trainClassifier(conn, cursor, tablename):
    query_traffic = "SELECT tweet from "+ tablename +" where ptraffic='y'"
    query_ntraffic = "SELECT tweet from "+ tablename +" where ptraffic<>'y'"
    
    cursor.execute(query_traffic)
    traffic_data = cursor.fetchall()
    
    cursor.execute(query_ntraffic)
    ntraffic_data = cursor.fetchall()

    #train
    
    #filtering words -- todo: smilies etc, make a seperate function for this
    data = []
    for words in traffic_data:
        words = words[0]
        filtered = [e.lower() for e in words.split() if len(e) >= 3]
        data.append((filtered, 'traffic'))

    for words in ntraffic_data:
        words = words[0]
        filtered = [e.lower() for e in words.split() if len(e) >= 3]
        data.append((filtered, 'not_traffic'))

    #getting features -- todo: create seperate function, find a better way(?)
    words = []
    for (tweet, label) in data:
        words.extend(tweet)
    
    words = nltk.FreqDist(words)
    features = words.keys()
    
    train_set = nltk.classify.apply_features(extract_features, data)
    nltk.NaiveBayesClassifier.train(train_set)

    

def extract_features(tweet):
    words = set(tweet)
    found_features = {}
    for word in features:
        found_features['contains(%s)' % word] = (word in tweet)
    return found_features


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
    tablename = 'labelled_tweets'

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
                    default=action,
                    help='The action the classifier will execute')
    parser.add_option('-t','--tablename',
                    dest='tablename',
                    default=tablename,
                    help='Training or testing or to-classify set tablename')

    (options, args) = parser.parse_args()

    opts = dict([ [k,v] for k,v in options.__dict__.iteritems() if not v is
        None ])
    sys.exit(main(*args,**opts))
