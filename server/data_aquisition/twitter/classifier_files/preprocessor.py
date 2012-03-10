import re
import nltk
import tldextract
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures


class preprocessor:

	def convert_links(self, tweet):
		"""Replace the urls in the tweets with their domains"""
		url_req_exp = re.compile(r'(?i)\b((?:(?:https?|ftp)://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\((?:[^\s()<>]+|(?:\(?:[^\s(?:)<>]+\)))*\))+(?:\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xc2\xab\xc2\xbb\xe2\x80\x9c\xe2\x80\x9d\xe2\x80\x98\xe2\x80\x99]))')
		try:
			strDif = 0
			index = 0
			numberOfURL = len(url_req_exp.findall(tweet))
			for m in url_req_exp.finditer(tweet):
				index = index + 1
				if m and index < numberOfURL and m.groups() > 0:
					url = tldextract.extract(m.group(0))
					repl = url.domain + '_' + url.tld
					url_start = m.start(1)-strDif
					url_end = m.end(1)-strDif
					tweet = tweet[0:url_start] + repl + tweet[url_end:len(tweet)]
					strDif = len(m.group(0)) - len(repl)
		except:
			exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
			sys.exit("The URL conversion failed! ->%s" % (exceptionValue))
		return tweet

					
	def replace_emoticons(self, emoticons_tweet):
		"""Replace the emoticons of the input string with the corresponding string"""
		#Many-to-one dictionary
		conv_dict_multi = { ('>:]', ':-)', ':)', ':o)', ':]', ':3', ':c', ':>', '=]', '8)', '=)', ':}', ':^)', ':)','|;-)', '|-o):', '>^_^<', '<^!^>', '^/^', '(*^_^*)', '(^<^)', '(^.^)', '(^?^)', '(^?^)', '(^_^.)', '(^_^)', '(^^)', '(^J^)', '(*^?^*)', '^_^', '(^-^)', '(?^o^?)', '(^v^)', '(^u^)', '(^?^)', '( ^)o(^ )', '(^O^)', '(^o^)', '(^?^)', ')^o^('):'_HAPPY_',
		('>:[', ':-(', ':(', ':-c', ':c', ':-<', ':<', ':-[', ':[', ':{', '>.>', '<.<', '>.<', '(\'_\')', '(/_;)', '(T_T)', '(;_;)', '(;_:)', '(;O;)', '(:_;)', '(ToT)', '(T?T)', '(>_<)', '>:\\', '>:/', ':-/', ':-.', ':/', ':\\', '=/', '=\\', ':S'):'_SAD_',
		('>:D', ':-', ':D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D', '=-3', '=3', '8-)', ':-))'):'_VERY_HAPPY_',
		('D:<', 'D:', 'D8', 'D;', 'D=', 'DX', 'v.v', '>:)', '>;)', '>:-)', ':\'-(', ' :\'-)', ':\')', ':-||'):'_VERY_SAD_'}
		#Convert to the one-to-one dict
		conv_dict = {}
		for k, v in conv_dict_multi.items():
			for key in k:
				conv_dict[key] = v
		#Replace the emoticons		
		for smiley, conv_str in conv_dict.iteritems():
			emoticons_tweet = emoticons_tweet.replace(smiley, conv_str)
		return emoticons_tweet
	
		
	def remove_puncuation(self, tweet):
		"""Remove all the puncuation except the symbol #,@,' from the tweet"""
		punctuation = re.compile(r'[-.?!,":;()|$%&*+/<=>[\]^`{}~]')
		#Replace with space the punctuation 
		return punctuation.sub(' ', tweet)
		
		
	def tokenazation(self, tweets_str, stopword_set):
		""" Lower the tweets (traffic and nontraffic), split them, remove the stopwords and the words with just one character """	
		tokenized_tweets = []
		for (tweets) in tweets_str:
				filtered_words = [e.lower() for e in tweets.split() if len(e) >= 2 and not e in stopword_set]
				tokenized_tweets.extend(filtered_words)
		return tokenized_tweets
		
		
	def remove_reg_expr(self, tokens):
		"""Remove the words we don't need to check"""
		data = []
		for tweets in tokens:
			#Remove from the tweets the "@username"
			req_exp = re.compile(r'@([A-Za-z0-9_]+)')
			tweets = req_exp.sub('',tweets)			
			if tweets!='':
				data.append(tweets)
		return data
	
		
	def lemmanazation(self,tokens):
		""" Lemmanaze the tokenized tweets (child ,children => child, child)"""
		wnl=nltk.WordNetLemmatizer()
		lemmas=[wnl.lemmatize(t) for t in tokens]
		return lemmas
		
		
	def include_bigrams(self, words, score_fn=BigramAssocMeasures.chi_sq, n=200):
		""" Find the bigramms and include them in the tokens """
		bigram_finder = BigramCollocationFinder.from_words(words)
		bigrams = bigram_finder.nbest(score_fn, n)
		return words + bigrams
		
		
	def preprocess(self, tweet, stopwords):
		tweet = self.convert_links(tweet)
		tweet = self.replace_emoticons(tweet)
		tweet = self.remove_puncuation(tweet)
		tweet = [tweet]
		tokens = []
		tokens = self.tokenazation(tweet,stopwords)
		tokens = self.remove_reg_expr(tokens)
		tokens = self.lemmanazation(tokens)
		tokens = self.include_bigrams(tokens)
		return tokens
		
		
