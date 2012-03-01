#! /usr/bin/env python

import os, os.path, re
import cPickle as pickle
import sys
import optparse
import ConfigParser
import nltk
from preprocessor import preprocessor
from evaluation import evaluation
from pg8000 import DBAPI

def main(*args,**opts):
	db = dict([ ['host',opts['host']], ['database',opts['database']],
		['user',opts['user']], ['password',opts['password']]])
	
	# The name of the table which have the labelled tweets
	tablename = 'labelled_tweets'
	
	# The tweet that need to be classified
	test_tweet = opts['text']
	
	# Enable for testin the data
	enable_evaluation = opts['test']

	cursor,conn = connectDB(**db)

	#Train and test the classifier
	classifier = trainClassifier(conn, cursor, tablename, test_tweet, enable_evaluation)

	#TO DO:: Implement cross-validation and ROC Cur from PyML

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

	
def dump_classifier(classifier, file_name):
	"""Save the classifier into a .pickle file for later use"""
	dirname = os.path.dirname(file_name)

	if dirname and not os.path.exists(dirname):
		print 'Creating directory %s' % dirname
		os.makedirs(dirname)

	print 'Dumping Naive Bayes classifier to %s' % (file_name)

	f = open(file_name, 'wb')
	pickle.dump(classifier, f)
	f.close()
	
def trainClassifier(conn, cursor, tablename, test_tweet, enable_evaluation):
	"""Train the Naive Bayes"""
	
	stop_words = []
	
	# Fetch all the stop words
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
	
	# Fetch all the traffic tweets
	try:
		query_pt = "SELECT tweet FROM "+ tablename +" WHERE ptraffic='y' ORDER BY tid ASC LIMIT 681"
		cursor.execute(query_pt)
		ttweets = cursor.fetchall()
	except:
		# Get the most recent exception
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		print "Select Error -> %s" % exceptionValue
		lastid="0"
	
	# Fetch all the non-traffic tweets	
	try:
		query_nt = "SELECT tweet FROM "+ tablename +" WHERE ntraffic='y' ORDER BY tid ASC LIMIT 681"
		cursor.execute(query_nt)
		nttweets = cursor.fetchall()
	except:
		# Get the most recent exception
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		print "Select Error -> %s" % exceptionValue
		lastid="0"
	
	# If the user chose to evaluate the classifier fetach more labelled tweets for testing
	if enable_evaluation == 'test':
		# Fetch all the traffic tweets for the evaluation
		try:
			query_pt = "SELECT tweet FROM "+ tablename +" WHERE ptraffic='y' ORDER BY tid DESC LIMIT 375"
			cursor.execute(query_pt)
			ttweets_test = cursor.fetchall()
		except:
			# Get the most recent exception
			exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
			print "Select Error -> %s" % exceptionValue
			lastid="0"
		
		# Fetch all the non-traffic tweets for the evaluation
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

		# Extract the features for the train set
		temp = []
		for i in range(len(combined_tweets)):
			temp.append(((features_extractor(combined_tweets[i][0])),combined_tweets[i][1]))
		train_set=temp
		
		# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		# >>>>>>>>>>>>>>>>>>>>>>>>>> TEST SET <<<<<<<<<<<<<<<<<<<<<<<<<<<
		# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		
		# If the user chose to evaluate the classifier create a test_set
		if enable_evaluation == 'test':
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
			
			# Extract the features for the test set
			temp = []
			for i in range(len(combined_tweets_test)):
				temp.append(((features_extractor(combined_tweets_test[i][0])),combined_tweets_test[i][1]))
			test_set=temp
		
		# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		# >>>>>>>>>>>>>>>>>>>>>>>>>> TRAIN THE CLASSIFIER <<<<<<<<<<<<<<<<<<<<<<<<<<<
		# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		
		# Train our classifier using the training set
		classifier = nltk.NaiveBayesClassifier.train(train_set)
		
		# Save the classifier in a .pickle file
		name = 'naive_bayes.pickle'
		fname = os.path.join(os.path.expanduser('~/nltk_data/classifiers'), name)
		dump_classifier(classifier, fname)
		
		# Classify the tweet
		test_tweet1 = preprocessor().preprocess(test_tweet,stop_words)
		test = features_extractor(test_tweet1)
		proba = classifier.prob_classify(test)
		print "\nThe tweet '%s' is about: %s with probability: %s\n" % (test_tweet, classifier.classify(test),proba.prob('traffic'))
		
		# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		# >>>>>>>>>>>>>>>>>>>>>>>>>> TEST THE CLASSIFIER <<<<<<<<<<<<<<<<<<<<<<<<<<<
		# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		
		# If the user chose to evaluate the classifier apply the evaluation techniques
		if enable_evaluation == 'test':
			evaluation(test_set,classifier)
	
		
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
    parser.add_option('-e','--text',
                    dest='text',
                    default="text",
                    help='Text to be classified')
    parser.add_option('-t','--test',
                    dest='test',
                    default='no',
                    help='True for evaluation')

    (options, args) = parser.parse_args()

    opts = dict([ [k,v] for k,v in options.__dict__.iteritems() if not v is
        None ])
    sys.exit(main(*args,**opts))

