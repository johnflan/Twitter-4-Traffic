#! /usr/bin/env python

from pg8000 import DBAPI
import sys
import optparse
import ConfigParser
import nltk
import re


features = []
stopwords = []

def main(*args,**opts):
    db = dict([ ['host',opts['host']], ['database',opts['database']],
        ['user',opts['user']], ['password',opts['password']]])

    cursor,conn = connectDB(**db)
    
    action = opts['action']

    if action=="train":
        #train and test the classifier
        classifier = trainClassifier(conn, cursor, opts['tablename'])

    #got to save the classifier somewhere so to use later
    elif action == "classify":
        print classifier.classify(extract_features(opts['text'].split()))

    else:
        print "\nPlease choose an action between train & classify\n"


def connectDB(**db):
    try:
        conn = DBAPI.connect(**db)
        cursor = conn.cursor()
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        sys.exit("Database connection failed! ->%s" % (exceptionValue))
    return cursor, conn

def filter_words(unfiltered_data):
    data = []
    for words in unfiltered_data:
        #add proper filtering..
        words = words[0].replace(",","").replace("%","")
        words = re.sub("\W"," ",words)
        filtered = [word.lower() for word in words.split() if not word in
                stopwords]
        data.append(filtered)
    return data

def add_label(data, label):
    labelled_data = []
    for row in data:
        labelled_data.append((row, label))
    return labelled_data

def find_features(data, number_of_features):
    #putting all tweet words in a list
    words = []
    for (tweet, label) in data:
        words.extend(tweet)

    #finally return the most common features (words) in this class
    words = nltk.FreqDist(words)
    famous_words = words.keys()
    if len(famous_words) > number_of_features:
        famous_words = famous_words[0:number_of_features]
    return famous_words


def trainClassifier(conn, cursor, tablename):
    temp = "SELECT count(*) from "+ tablename +" where ptraffic='y'"
    cursor.execute(temp)
    limit = str(cursor.fetchone()[0])

    queries = []
    queries.append("SELECT tweet from "+ tablename +
            " where ptraffic='y'")
    #queries.append("SELECT tweet from "+ tablename +" where ntraffic='y' limit "+limit)
    queries.append("SELECT tweet from "+ tablename +
            " where ptraffic<>'y' and unclear<>'y' limit "+limit)
    #queries.append("SELECT tweet from "+ tablename +" where robot='y' limit "+limit)
    labels = ['traffic', 'not_traffic', 'robot']
    
    cursor.execute("SELECT word FROM stop_words limit 50")
    rows = cursor.fetchall()
    stopwords = []
    for row in rows:
        row = row[0]
        stopwords.append(row)

    data = []
    for i in range(len(queries)):
        cursor.execute(queries[i])
        #filter words here
        temp_data = cursor.fetchall()
        filtered = filter_words(temp_data)
        data.extend(add_label(filtered,labels[i]))

    #train

    features.extend(find_features(data, 100))

    train_set = nltk.classify.apply_features(extract_features, data)
    classifier = nltk.NaiveBayesClassifier.train(train_set)

    #test in train
    print nltk.classify.accuracy(classifier, train_set)

    #todo: test in test set

    return classifier


def extract_features(tweet):
    words = filter_words(tweet)
    found_features = {}
    for word in features:
        found_features['contains(%s)' % word] = (word in words)
    return found_features



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
