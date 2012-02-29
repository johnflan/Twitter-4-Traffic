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

def main(*args,**opts):
	db = dict([ ['host',opts['host']], ['database',opts['database']],
		['user',opts['user']], ['password',opts['password']]])

	#The tweet that need to be classified
	test_tweet = opts['text']

	cursor,conn = connectDB(**db)

	#Train and test the classifier
	classifier = trainClassifier(conn, cursor, opts['tablename'], test_tweet)

	#TO DO:: Save the classifier in a file (.pkl) so to use later. http://docs.python.org/library/shelve.html#module-shelve
	#TO DO:: Apply more tests for the evaluation
	#TO DO:: Test performance with lemmanization
	

def connectDB(**db):
	"""Connect to the Database"""
	try:
		conn = DBAPI.connect(**db)
		cursor = conn.cursor()
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		sys.exit("Database connection failed! ->%s" % (exceptionValue))
	return cursor, conn

	
	
def features_extractor(words):
	"""Create dictionaries mapping a feature name to a feature value(TRUE)."""
	return dict([(word, True) for word in words])

	
def add_label(data, label):
	"""Include the label for each tweet in the same list"""
	labelled_data = []
	for row in data:
		labelled_data.append((row, label))
	return labelled_data

	
def trainClassifier(conn, cursor, tablename, test_tweet):
	"""Train the Naive Bayes"""
	
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
		query_pt = "SELECT tweet FROM "+ tablename +" WHERE ptraffic='y' ORDER BY tid ASC LIMIT 681"
		cursor.execute(query_pt)
		ttweets = cursor.fetchall()
	except:
		# Get the most recent exception
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		print "Select Error -> %s" % exceptionValue
		lastid="0"
	
	#Fetch all the non-traffic tweets	
	try:
		query_nt = "SELECT tweet FROM "+ tablename +" WHERE ntraffic='y' ORDER BY tid ASC LIMIT 681"
		cursor.execute(query_nt)
		nttweets = cursor.fetchall()
	except:
		# Get the most recent exception
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		print "Select Error -> %s" % exceptionValue
		lastid="0"
	
	
	#Fetch all the traffic tweets
	try:
		query_pt = "SELECT tweet FROM "+ tablename +" WHERE ptraffic='y' ORDER BY tid DESC LIMIT 375"
		cursor.execute(query_pt)
		ttweets_test = cursor.fetchall()
	except:
		# Get the most recent exception
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		print "Select Error -> %s" % exceptionValue
		lastid="0"
	
	#Fetch all the non-traffic tweets	
	try:
		query_nt = "SELECT tweet FROM "+ tablename +" WHERE ntraffic='y' ORDER BY tid DESC LIMIT 375"
		cursor.execute(query_nt)
		nttweets_test = cursor.fetchall()
	except:
		# Get the most recent exception
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		print "Select Error -> %s" % exceptionValue
		lastid="0"
		
		
	try:
		# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		# >>>>>>>>>>>>>>>>>>>>>>>>>> TRAIN SET <<<<<<<<<<<<<<<<<<<<<<<<<<
		# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		# Apply preprocessing on the traffic tweets for the train set
		data=[]
		for text in ttweets:
			temp = preprocessor().preprocess(text[0],stop_words)
			data.append(temp)
		traffic_tweets=add_label(data, 'traffic')
		
		# Apply preprocessing on the non-traffic tweets for the train set
		data=[]
		for text in nttweets:
			temp = preprocessor().preprocess(text[0],stop_words)
			data.append(temp)
		nontraffic_tweets=add_label(data, 'nontraffic')
		
		# Merge the tweets for the train set
		combined_tweets = traffic_tweets + nontraffic_tweets

		#Extract the features for the train set
		temp = []
		for i in range(len(combined_tweets)):
			temp.append(((features_extractor(combined_tweets[i][0])),combined_tweets[i][1]))
		train_set=temp
		# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		# >>>>>>>>>>>>>>>>>>>>>>>>>> TEST SET <<<<<<<<<<<<<<<<<<<<<<<<<<<
		# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		# Apply preprocessing on the traffic tweets for the test set
		data=[]
		for text in ttweets_test:
			temp = preprocessor().preprocess(text[0],stop_words)
			data.append(temp)
		traffic_tweets_test=add_label(data, 'traffic')
		
		# Apply preprocessing on the non-traffic tweets for the test set
		data=[]
		for text in nttweets_test:
			temp = preprocessor().preprocess(text[0],stop_words)
			data.append(temp)
		nontraffic_tweets_test=add_label(data, 'nontraffic')
		
		# Merge the tweets for the test set
		combined_tweets_test = traffic_tweets_test + nontraffic_tweets_test
		
		#Extract the features for the test set
		temp = []
		for i in range(len(combined_tweets_test)):
			temp.append(((features_extractor(combined_tweets_test[i][0])),combined_tweets_test[i][1]))
		test_set=temp
		
		# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		# >>>>>>>>>>>>>>>>>>>>>>>>>> TRAIN THE CLASSIFIER <<<<<<<<<<<<<<<<<<<<<<<<<<<
		# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		
		#Train our classifier using the training set
		classifier = nltk.NaiveBayesClassifier.train(train_set)
		
		#Classify the tweet
		test = features_extractor(test_tweet.lower().split())
		print "\nThe tweet '%s' is about: %s \n" % (test_tweet, classifier.classify(test))
		
		#Evaluation of the classification
		print 'accuracy:', nltk.classify.util.accuracy(classifier, test_set)
		print nltk.classify.accuracy(classifier, train_set)
		classifier.show_most_informative_features()
		
	except:	
		# Get the most recent exception
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		print "Error -> %s" % exceptionValue
		lastid="0"
	


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

