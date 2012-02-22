#! /usr/bin/env python

import sys
import optparse
import ConfigParser
import nltk
import re
from pg8000 import DBAPI
from nltk.corpus import stopwords
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
	#TO DO:: Better tokenization (remove ", . /" etc from the words) and ( req. expr. vs nltk.word_tokenize() )
	#TO DO:: Convert emotions to strings eg. :) -> _smile_ ,  :( -> _sad_
	#TO DO:: Apply more tests for the evaluation
	#TO DO:: Research if the ordering on the bag of words improve the accuracy
	#TO DO:: Test performance with lemmanization
	#TO DO:: Apply basic text modifications on the tweets that they need to be classified
	

def connectDB(**db):
	"""Connect to the Database"""
	try:
		conn = DBAPI.connect(**db)
		cursor = conn.cursor()
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		sys.exit("Database connection failed! ->%s" % (exceptionValue))
	return cursor, conn


def filter_tweets(unfiltered_tweets):
	"""Remove the characters/words we don't need to check"""
	data = []
	stopset = set(stopwords.words('english'))
	for tweets in unfiltered_tweets:
		# remove from the tweets the ",)"
		tweets = tweets[0].replace(",)","")
		#remove from the tweets the "@username"
		req_exp = re.compile(r'@([A-Za-z0-9_]+)')
		tweets = req_exp.sub('',tweets)
		data.append(tweets)
	return data


def form_tweets(tt,ntt):
	""" Lower the tweets (traffic and nontraffic), split them and remove the remove the stopwords and the words with just one character """	
	stopword_set = set(stopwords.words('english'))
	formed_tweets = []
       	for (tweets, label) in tt + ntt:
               	filtered_words = [e.lower() for e in tweets.split() if len(e) >= 2 and not e in stopword_set]
                formed_tweets.append((filtered_words, label))
	return formed_tweets

	
def features_extractor(words):
	"""Create dictionaries mapping a feature name to a feature value(TRUE)."""
	return dict([(word, True) for word in words])

	
def add_label(data, label):
	"""Include the label for each tweet in the same list"""
	labelled_data = []
	for row in data:
		labelled_data.append((row, label))
	return labelled_data

	
def dist_words_order(tweets):
	"""Create a list of the distinct words ordered descending by frequency of appearance"""
 	dist_words = []
	for (word, label) in tweets:
		dist_words.extend(word)
	return word_freq(dist_words)


def word_freq(d_words):
	"""Find the frequently of each word"""
	freq_words  = nltk.FreqDist(d_words)
	w_features = freq_words.keys()
	return w_features

	
def include_bigrams(words, score_fn=BigramAssocMeasures.chi_sq, n=200):
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn, n)
    return features_extractor(words + bigrams)

	
def trainClassifier(conn, cursor, tablename, test_tweet):
	"""Train the Naive Bayes"""
	
	stopset = set(stopwords.words('english'))
	
	#Fetch all the traffic tweets
	try:
		query_pt = "SELECT tweet FROM "+ tablename +" WHERE ptraffic='y' LIMIT 50"
		cursor.execute(query_pt)
		ttweets = cursor.fetchall()
	except:
		# Get the most recent exception
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		print "Select Error -> %s" % exceptionValue
		lastid="0"
	
	#Fetch all the non-traffic tweets	
	try:
		query_nt = "SELECT tweet FROM "+ tablename +" WHERE ntraffic='y' LIMIT 50"
		cursor.execute(query_nt)
		nttweets = cursor.fetchall()
		# print "\n\n NTWEETS"
		# print (nttweets)
		# print "\n"
	except:
		# Get the most recent exception
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		print "Select Error -> %s" % exceptionValue
		lastid="0"
	
	try:	
		#Filter the tweets and add the label in the list for each tweet
		data = []
		data = filter_tweets(ttweets)
		traffic_tweets=add_label(data, 'traffic')
		data = []
		data = filter_tweets(nttweets)
		nontraffic_tweets = add_label(data, 'nontraffic')
			
		#Reform the tweets in a usable way and create an ordered list of the distinct words
		ftweets = []
		ftweets = form_tweets(traffic_tweets, nontraffic_tweets)
		
		#Extract the features
		temp = []
		for i in range(len(ftweets)):
			temp.append(((include_bigrams(ftweets[i][0])),ftweets[i][1]))
		train_set=temp

		#Train our classifier using the training set
		classifier = nltk.NaiveBayesClassifier.train(train_set)
		
		#Classify the tweet
		test = features_extractor(test_tweet.lower().split())
		print "\nThe tweet '%s' is about: %s \n" % (test_tweet, classifier.classify(test))
		
		#Evaluation of the classification
		#print classifier.show_most_informative_features(10)
		#print nltk.classify.accuracy(classifier, train_set)
		
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

