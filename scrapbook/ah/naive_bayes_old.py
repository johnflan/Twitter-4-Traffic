#! /usr/bin/env python

from pg8000 import DBAPI
import sys
import optparse
import ConfigParser
import nltk
import re


def main(*args,**opts):
    db = dict([ ['host',opts['host']], ['database',opts['database']],
        ['user',opts['user']], ['password',opts['password']]])

    cursor,conn = connectDB(**db)
    
    action = opts['action']

    #if action=="train":
        #train and test the classifier"""
    classifier = trainClassifier(conn, cursor, opts['tablename'])
	
    #got to save the classifier somewhere so to use later
   # elif action == "classify":
 #       print classifier.classify(extract_features(opts['text'].split()))

   # else:
    #    print "\nPlease choose an action between train & classify\n"
#	"""

def connectDB(**db):
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
	for tweets in unfiltered_tweets:
        	# remove from the tweet the ",)"
                tweets = tweets[0].replace(",)","")
                #remove from the tweet the "@username"
                req_exp = re.compile(r'@([A-Za-z0-9_]+)')
                tweets = req_exp.sub('',tweets)
                data.append(tweets)
	return data


def form_tweets(tt,ntt):
	""" Lower the tweets (traffic and nontraffic), split them and keep the words with more than 1 character """	
	formed_tweets = []
       	for (tweets, label) in tt + ntt:
               	filtered_words = [e.lower() for e in tweets.split() if len(e) >= 2]
                formed_tweets.append((filtered_words, label))
	return formed_tweets


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
	return word_features(dist_words)


def word_features(d_words):
	"""Find the frequently of each word"""
	d_words  = nltk.FreqDist(d_words)
	print "\n>>>>>>>>>>>>>>>>FREQDIST\n"
	print (d_words)
	print "\n\n"
	w_features = d_words.keys()
	return w_features


"""def tweet_features(ftweets):
	#Extraction of the tweets
	print "inside"
	word_features = dist_words_order(ftweets)
	print "WORD FEATURES: " % word_features
	tweets_words = set(ftweets)
	features = {}
	for word in word_features:
		features['contains(%s)' % word] = (word in tweets_words)
	return features
"""
	
def trainClassifier(conn, cursor, tablename):
	"""Train the Naive Bayes"""
	#Fetch all the traffic tweets
	try:
		query_pt = "SELECT tweet FROM "+ tablename +" WHERE ptraffic='y' LIMIT 5"
		cursor.execute(query_pt)
		ptweets = cursor.fetchall()
		print (ptweets)
	except:
		# Get the most recent exception
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		print "Select Error -> %s" % exceptionValue
		lastid="0"
	
	#Fetch all the non-traffic tweets	
	try:
		query_nt = "SELECT tweet FROM "+ tablename +" WHERE ntraffic='y' LIMIT 5"
		cursor.execute(query_nt)
		ntweets = cursor.fetchall()
		print "\n\n NTWEETS"
		print (ntweets)
		print "\n\n\n"
	except:
		# Get the most recent exception
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
		print "Select Error -> %s" % exceptionValue
		lastid="0"
	
	try:	
		#Filter the tweets and add the label in the list for each tweet
		data = []
		data = filter_tweets(ptweets)
		traffic_tweets=add_label(data, 'traffic')
		data = []
		data = filter_tweets(ntweets)
		nontraffic_tweets = add_label(data, 'nontraffic')
			
		#Reform the tweets in a usable way and create an ordered list of the distinct words
		ftweets = []
		ftweets = form_tweets(traffic_tweets, nontraffic_tweets)
		
		# print "\n\n FTWEETS "
		# print (ftweets)
		# print "\n\n"
		
		#????I can do it in previous step (add_label)????
		temp = []
		for i in range(len(ftweets)):
			
			for j in range(len(ftweets[i][0])):
				temp.append(((ftweets[i][0][j]),ftweets[i][1]))
		ftweets=temp
		# print "TEMP : \n"
		# print(ftweets)
		# print "\n\n"
		word_features = dist_words_order(ftweets)
                print "WORD FEATURES: %s" % word_features


		def tweet_features(formed_tweets):
        		"""Extraction of the tweet features"""
        		tweets_words = set(formed_tweets)
        		features = {}
        		for word in word_features:
               			 features['contains(%s)' % word] = (word in tweets_words)		 
		        return features
		
		
		#Find the training set
		#featuresets = [(tweet_features(n), g) for (n,g) in ftweets]
		train_set = nltk.classify.apply_features(tweet_features, ftweets)
        	
		# print "\n\n TRAIN SET "
	        # print(train_set)
		# print "\n\n"
		
		#Train our classifier using the training set
		classifier = nltk.NaiveBayesClassifier.train(train_set)
		#print nltk.classify.accuracy(classifier, train_set)
		test = 'm25'
		print classifier.classify(tweet_features(test))
		print classifier.show_most_informative_features(10)
		
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

