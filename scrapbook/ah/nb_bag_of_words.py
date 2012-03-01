#! /usr/bin/env python

import os, os.path, re
import cPickle as pickle
import sys
import optparse
import ConfigParser
import nltk
import collections
from preprocessor import preprocessor
from pg8000 import DBAPI

def main(*args,**opts):
	db = dict([ ['host',opts['host']], ['database',opts['database']],
		['user',opts['user']], ['password',opts['password']]])
	
	# The name of the table which have the labelled tweets
	tablename = 'labelled_tweets'
	
	# The tweet that need to be classified
	test_tweet = opts['text']

	cursor,conn = connectDB(**db)

	#Train and test the classifier
	classifier = trainClassifier(conn, cursor, tablename, test_tweet)

	#TO DO:: Save the classifier in a file (.pkl) so to use later. http://docs.python.org/library/shelve.html#module-shelve	
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
	
def trainClassifier(conn, cursor, tablename, test_tweet):
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
		query_nt = "SELECT tweet FROM "+ tablename +" WHERE ntraffic='y' ORDER BY tid ASC LIMIT 10875"
		cursor.execute(query_nt)
		nttweets = cursor.fetchall()
	except:
		# Get the most recent exception
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		print "Select Error -> %s" % exceptionValue
		lastid="0"
	
	
	# Fetch all the traffic tweets
	try:
		query_pt = "SELECT tweet FROM "+ tablename +" WHERE ptraffic='y' ORDER BY tid DESC LIMIT 375"
		cursor.execute(query_pt)
		ttweets_test = cursor.fetchall()
	except:
		# Get the most recent exception
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		print "Select Error -> %s" % exceptionValue
		lastid="0"
	
	# Fetch all the non-traffic tweets	
	try:
		query_nt = "SELECT tweet FROM "+ tablename +" WHERE ntraffic='y' ORDER BY tid DESC LIMIT 3625"
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
		print "\nThe tweet '%s' is about: %s \n" % (test_tweet1, classifier.classify(test))
		
		# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		# >>>>>>>>>>>>>>>>>>>>>>>>>> TEST THE CLASSIFIER <<<<<<<<<<<<<<<<<<<<<<<<<<<
		# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		
		referenceSet = collections.defaultdict(set)
		testSet = collections.defaultdict(set)
		referenceSet_cm = []
		testSet_cm = []
		
		for index, (tweets, actualLabel) in enumerate(test_set):
			referenceSet[actualLabel].add(index)
			referenceSet_cm.append(actualLabel)
			predictedLabel = classifier.classify(tweets)
			testSet[predictedLabel].add(index)
			testSet_cm.append(predictedLabel)

		# Evaluation of the classification
		# Accuracy is the percentage of the correct classifications of the test_test (fraction of the labelled data)
		# Recall describes the completeness of the retrieval. It is defined as the portion of the positive examples retrieved by the process versus the  
		# total  number of existing positive examples (including the ones not retrieved by the process). 
		# Precision describes the actual accuracy of the retrieval, and is defined as the portion of the positive examples that exist in the total number of 
		# examples retrieved.
		
		print 'Accuracy of the classifier:  ', nltk.classify.util.accuracy(classifier, test_set)
		print '\nTraffic precision:           ', nltk.metrics.precision(referenceSet['traffic'], testSet['traffic'])
		print 'Traffic recall:              ', nltk.metrics.recall(referenceSet['traffic'], testSet['traffic'])
		print 'Traffic F-measure:           ', nltk.metrics.f_measure(referenceSet['traffic'], testSet['traffic'])
		print '\nNon-Traffic precision:       ', nltk.metrics.precision(referenceSet['nontraffic'], testSet['nontraffic'])
		print 'Non-Traffic recall:          ', nltk.metrics.recall(referenceSet['nontraffic'], testSet['nontraffic'])
		print 'Non-Traffic F-measure:       ', nltk.metrics.f_measure(referenceSet['nontraffic'], testSet['nontraffic'])
		print "\n"
		
		# Find the Confusion Matrix for the test set
		cm = nltk.ConfusionMatrix(referenceSet_cm, testSet_cm)
		print cm.pp(sort_by_count=True, show_percents=True, truncate=9) 
		
		# Show the 10 features with the greatest gain
		# classifier.show_most_informative_features()
		
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

    (options, args) = parser.parse_args()

    opts = dict([ [k,v] for k,v in options.__dict__.iteritems() if not v is
        None ])
    sys.exit(main(*args,**opts))

