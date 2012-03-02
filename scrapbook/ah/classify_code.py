import nltk.data
from classifier_files.preprocessor import preprocessor

# Classify the text from the Search API
classifier = nltk.data.load("/srv/t4t/classifier_files/naive_bayes.pickle")
text = preprocessor().preprocess(textt,[])
label = features_extractor(text)

# Find its Probability
if label == 'traffic':
	probability_dict  = classifier.prob_classify(test)
	probability = probability_dict.prob('traffic')

#