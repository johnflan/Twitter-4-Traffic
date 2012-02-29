#! /usr/bin/env python

import sys
import optparse
import ConfigParser
import nltk
import re
from preprocessor import preprocessor
from pg8000 import DBAPI
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from PyML import *

def main(*args,**opts):
    db = dict([ ['host',opts['host']], ['database',opts['database']],
        ['user',opts['user']], ['password',opts['password']]])

    #The tweet that need to be classified
    test_tweet = opts['text']

    cursor,conn = connectDB(**db)

    #Train and test the classifier
    classifier = trainClassifier(conn, cursor, opts['tablename'])

    #TO DO:: Save the classifier in a file.


def connectDB(**db):
    """Connect to the Database"""
    try:
        conn = DBAPI.connect(**db)
        cursor = conn.cursor()
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        sys.exit("Database connection failed! ->%s" % (exceptionValue))
    return cursor, conn


def filter_and_dict(table_of_strings, stop_words):
        data = []
        for tweet in table_of_strings:
            tweet_words = preprocessor().preprocess(tweet[0], stop_words)
            temp_dict = {}
            for word in tweet_words:
                if word in temp_dict.keys():
                    temp_dict[word] = temp_dict[word] + 1
                else:
                    temp_dict[word] = 1
            data.append(temp_dict)
        return data


def trainClassifier(conn, cursor, tablename):
    """Train Support Vector Machine"""

    stop_words = []

    # Fetch all stop_words
    # try:
        # query_sw = "SELECT word FROM stop_words limit 35"
        # cursor.execute(query_sw)
        # sw = cursor.fetchall()
        # stop_words = filter_tweets(sw)
        # print(stop_words)
    # except:
        # Get the most recent exception
        # exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        # print "Select Error -> %s" % exceptionValue
        # lastid="0"

    #Fetch all the traffic tweets
    try:
        query_pt = "SELECT tweet FROM "+ tablename +" WHERE ptraffic='y' ORDER BY tid ASC LIMIT 1506"
        cursor.execute(query_pt)
        ttweets = cursor.fetchall()
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        print "Select Error -> %s" % exceptionValue
        lastid="0"

    #Fetch all the non-traffic tweets
    try:
        query_nt = "SELECT tweet FROM "+ tablename +" WHERE ntraffic='y' ORDER BY tid ASC LIMIT 1506"
        cursor.execute(query_nt)
        nttweets = cursor.fetchall()
    except:
        # Get the most recent exception
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        print "Select Error -> %s" % exceptionValue
        lastid="0"

    #try:
        #Filter the tweets and add the label in the list for each tweet

    traffic_data = filter_and_dict(ttweets, stop_words)
    ntraffic_data = filter_and_dict(nttweets, stop_words)

    tr_l = int(len(traffic_data)*2.0/3.0)
    ntr_l = int(len(ntraffic_data)*2.0/3.0)

    train_labels = ['ptraffic'] * tr_l + ['ntraffic'] * ntr_l
    train_data = traffic_data[0:tr_l] + ntraffic_data[0:ntr_l]

    train_set = SparseDataSet(train_data, L=train_labels)


    test_labels = ['ptraffic'] * (len(traffic_data) - tr_l) + ['ntraffic'] * (len(ntraffic_data) - ntr_l)
    test_data = traffic_data[tr_l:len(traffic_data)] + ntraffic_data[ntr_l:len(ntraffic_data)]

    test_set = SparseDataSet(test_data, L=test_labels)


    print "\n\nTRAIN SET INFO\n"
    print train_set

    print "\n\nTEST SET INFO\n"
    print test_set

    classifier = SVM()

    #train our classifier using cross validation
    classifier.train(train_set, saveSpace = False)
    result = classifier.test(test_set)
    print "\n\nTRAINING RESULT\n"
    print result

    classifier.save('classifier_svm.txt')
    print "\n\nSaved\n"
    loaded = SVM()
    loaded.load('classifier_svm.txt',train_set)
    print "\n\nLOADED\n"
    r = loaded.test(test_set)
    print r

        #test_tweet = "Traffic is hell"
        #Classify the tweet
        #test = filter_and_dict(test_tweet, stop_words)

        #print "\nThe tweet '%s' is about: %s \n" % (test_tweet, classifier.test(test))

        #print "\n\n\n"
        #print classifier

    #except:
        # Get the most recent exception
        #exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        #print "Error -> %s" % exceptionValue
        #lastid="0"



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
                    help='Training and testing set tablename')
    parser.add_option('-e','--text',
                    dest='text',
                    default="text",
                    help='Text to be classified')

    (options, args) = parser.parse_args()

    opts = dict([ [k,v] for k,v in options.__dict__.iteritems() if not v is
        None ])
    sys.exit(main(*args,**opts))

