import nltk.data
from preprocessor import preprocessor

# Classify the text from the Search API
classifier = nltk.data.load("classifiers/naive_bayes.pickle")
text = preprocessor().preprocess(textt,[])
label = classifier.classify(features_extractor(text))

# Find its Probability
if label == 'traffic':
	probability_dict  = classifier.prob_classify(test)
	probability = probability_dict.prob('traffic')

#