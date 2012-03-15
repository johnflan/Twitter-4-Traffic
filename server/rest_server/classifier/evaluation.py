# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# >>>>>>>>>>>>>>>>>>>>>>>>>> TEST THE CLASSIFIER <<<<<<<<<<<<<<<<<<<<<<<<<<<
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
import nltk
import collections

def evaluation(test_set, classifier):
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