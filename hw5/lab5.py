#
# 6.034 Fall 2010 lab 5
# Name:
# Email:
#
from data_reader import *
from boost import *
from orange_for_6034 import *
from neural_net_data import *
import neural_net

SVM_TYPE = orange.SVMLearner.C_SVC

# Senate and House Data
# These should be familiar by now.
senate_people = read_congress_data('S110.ord')
senate_votes = read_vote_data('S110desc.csv')

house_people = read_congress_data('H110.ord')
house_votes = read_vote_data('H110desc.csv')

last_senate_people = read_congress_data('S109.ord')
last_senate_votes = read_vote_data('S109desc.csv')

house_1796 = read_congress_data('H004.ord')
house_1796_votes = read_vote_data('H004desc.csv')


# The first step is to complete the boosting code in boost.py. None of the
# following steps will work without it.
#
# Once you've done that, the following line should make a boost classifier
# that learns about the 4th House of Representatives (1795-1796).

boost_1796 = BoostClassifier(make_vote_classifiers(house_1796_votes),
                             house_1796, standardPartyClassifier)
# standardPartyClassifier returns 1 if Republican, -1 Otherwise.

# You will need to train it, however. You can change the number of steps here.
boost_1796.train(100)

#for cas in boost_1796.classifiers:
#    if "NEWSPAPERS;" in cas.__str__().strip().split():
#        print cas

# Once you have run your boosting classifier for a sufficient number of steps
# on the 4th House of Representatives data, it should tell you how it believes
# Republicans and Federalists generally voted on a range of issues. Which way
# does it predict a Republican would vote on the amendment to require
# "newspapers to be sufficiently dried before mailing"? ('yes' or 'no')

republican_newspaper_vote = 'no'

# In the 4th House of Representatives, which five representatives were
# misclassified the most while training your boost classifier?
#
# You should answer this question by defining the following function.
# It should return five names of legislators, in the format that comes from
# the legislator_info function. The tests will check the function, not just
# its output in this case.
import numpy as np

def most_misclassified(classifier, n=5):
    """
    Given a trained boosting classifier, return the n data points that were
    misclassified the most (based on their final weights). The
    most-misclassified datum should be at the beginning of the list.

	You will need to use the "legislator_info(datum)" function to put your
	output in the correct format.

	classifier: instance of Classifier -- used to classify the data
	n: int -- the number of most-misclassified data points to return

	returns: list of data points (each passed through legislator_info) that were
			 misclassified most often
    """

    sort_low_to_high = np.argsort(classifier.data_weights)

    misclass = []
    for i in range(n):
        idx = sort_low_to_high[-(i+1)]
        misclass.append(legislator_info(classifier.data[idx]))

    return misclass

# The following line is used by the tester; please leave it in place!
most_misclassified_boost_1796 = lambda n: most_misclassified(boost_1796, n)

# print most_misclassified_boost_1796(5)

# Now train a similar classifier on the 110th Senate (2007-2008).
# How does it say a Republican would vote on Cardin Amdt No. 3930; To modify
# the sunset provision (whatever that is)?

boost = BoostClassifier(make_vote_classifiers(senate_votes), senate_people,
  standardPartyClassifier)
boost.train(20)

#print "ANALYZING MODERN SENATE"
#for cas in boost.classifiers:
#    if "sunset" in cas.__str__().strip().split():
#        print cas
#raise

republican_sunset_vote = 'no'

# Which five Senators are the most misclassified after training your
# classifier? (Again, the tester will test the function, not the answer you
# print out here.)

# The following line is used by the tester; please leave it in place!
most_misclassified_boost = lambda n: most_misclassified(boost, n)

# print most_misclassified_boost(5)




########################################################################
def show_decisions(learner, data):
    print "  "+learner.name+":"
    classifier = learner(data) # Train on the data
    print "  "+str(classifier)
    total = 0
    for i in range(len(data)): # Test each of the same data points
        decision = classifier(data[i])
        probabilities = classifier(data[i], orange.Classifier.GetProbabilities)
        correct = (decision == data[i].getclass())
        if correct:
            total += 1
        print ("    %d: %5.3f -> %s (should be %s) %scorrect" %
               (i+1, probabilities[1], decision, data[i].getclass(),
                ("" if correct else "in")))
    print "    accuracy on training data: %1.2f" % (float(total)/len(data))

def describe_and_classify(filename, learners):
    data = orange.ExampleTable(filename)
    print "Classes:",len(data.domain.classVar.values)
    print "Attributes:",len(data.domain.attributes)

    # obtain class distribution
    c = [0] * len(data.domain.classVar.values)
    for e in data:
        c[int(e.getclass())] += 1
    print "Instances:", len(data), "total",
    for i in range(len(data.domain.classVar.values)):
        print ",", c[i], "with class", data.domain.classVar.values[i],
    print
    print "Possible classes:", data.domain.classVar.values

    for name in learners:
        show_decisions(learners[name], data)

    print "Decision Tree boundaries:"
    orngTree.printTxt(learners["dt"](data))

    # Now we'll cross-validate with the same learners.
    print
    print "Accuracy with cross-validation:"


    classifiers = [learners[k] for k in learners]
    results = orngTest.crossValidation(classifiers, data,
                                       folds=min(10,len(data)))

    confusion_matrices = orngStat.confusionMatrices(results)
    #f_scores   = orngStat.F1(confusion_matrices)
    #print f_scores
    # http://en.wikipedia.org/wiki/F_score
    accuracies = orngStat.CA(results)
    # http://en.wikipedia.org/wiki/Accuracy
    brierscores= orngStat.BrierScore(results)
    # http://en.wikipedia.org/wiki/Brier_score
    ROC_areas  = orngStat.AUC(results) # Area under the ROC curve
    # http://en.wikipedia.org/wiki/ROC_curve

    # NOTE: many other measurements are available.

    print "  Confusion Matrices:"
    for name in learners:
        classifier = learners[name]
        i = classifiers.index(classifier)
        print "  %5s: %s" % (name, confusion_matrices[i])

    print "  Classifier   accuracy   Brier       AUC"
    for name in learners:
        classifier = learners[name]
        i = classifiers.index(classifier)
        print ("  %-12s %5.3f      %5.3f       %5.3f" %
               (name, accuracies[i], brierscores[i], ROC_areas[i]))

# Note that it's the same declarations as above, just without the data

learners = {
    "maj" : orange.MajorityLearner(), # a useful baseline
    "dt"  : orngTree.TreeLearner(sameMajorityPruning=1, mForPruning = 2),
    "knn" : orange.kNNLearner(k = 10),
    "svml": orange.SVMLearner(kernel_type = orange.SVMLearner.Linear,
                              probability = True, svm_type=SVM_TYPE),
    "svmp3":orange.SVMLearner(kernel_type = orange.SVMLearner.Polynomial,
                              degree = 3,
                              probability = True, svm_type=SVM_TYPE),
    "svmr": orange.SVMLearner(kernel_type = orange.SVMLearner.RBF,
                              probability = True, svm_type=SVM_TYPE),
    "svms": orange.SVMLearner(kernel_type = orange.SVMLearner.Sigmoid,
                              probability = True, svm_type=SVM_TYPE),
    "nb": orange.BayesLearner(),

    #"boost":orngEnsemble.BoostedLearner(orngTree.TreeLearner()),
    # http://www.ailab.si/orange/doc/modules/orngEnsemble.htm
    # but it doesn't work...

    # you can use SVMLearner.Custom to make your own, of course.
    }
learners["maj"].name = "Majority classifier"
learners["dt"].name = "Decision Tree classifier"
learners["knn"].name = "k-Nearest Neighbors classifier"
learners["svml"].name = "Support Vector Machine classifier with linear kernel"
learners["svmp3"].name = "Support Vector Machine classifier with degree 3 polynomial kernel"
learners["svmr"].name = "Support Vector Machine classifier with radial basis kernel"
learners["svms"].name = "Support Vector Machine classifier with sigmoid kernel"
learners["nb"].name = "Naive Bayes classifier"
#FIXME: learners["034b"].name = "Our boosting classifier for party id datasets"
#learners["boost"].name = "Boosted decision trees classifier"

"""
if __name__ == "__main__":
    describe_and_classify("vampires", learners)
"""
# For the vampire dataset, what variable does the id tree query, that our
# algorithm in class did not?
vampires_idtree_odd = "accent"

# For the vampire dataset, which classifier does the worst when tested on just
# the data on which it was trained?
vampires_worst_on_training = 'svmr'
# Is it actually doing badly, or is it just confused?

# For the vampire dataset, which classifier does the worst when cross-validated?
vampires_worst_on_test = 'svmr'
"""
I get svmr as the worst possible classifier.
SVMR has the worst accuracy, worst Brier score, and second worst AUC score.
SVMS is 50-percent acurate, much lower Brier score, and third best AUC score.

I can't figure out why SVMR is considered the worst classifier by them.

The hw pdf mentions that classifier performance is architecture dependent.
In the face of that fact, I believe this is a case where my classifier differs
from their architecture. Not too surprising given it's nearly 7 years old at
ths point.

In the interest of fairness, I'm leaving my answer as is, despite the fact it
fails the test. If anyone else reads this, bear this in mind.
"""

# worst is weird. Accuracy is just how many you got right. 1 is good, 0 is bad.
# brier score is Square-Distance of prediction from actual value. 1 is bad, 0 is good.
# For brier score, more positive area unde curve, better. So 1 is good, 0 is bad

# Which of the above classifiers has the best Brier distance to the true answers
# in ten-fold cross-validation for the H004 dataset?

best_brier_for_h004 = 'maj'

# Just looking at the confusion matrices, what is the minimum number
# of data points that must have been differently classified between
# the best classifier and the second-best classifier for the H004 data
# set?

min_disagreement_h004 = 2

# Which bill was the most divisive along party lines in the H004 data
# set, according to the classification tree (id tree)?

most_divisive_h004 = '2'



################################################################
# Now let's see if we can do even better on the H004 dataset, by
# boosting the results of the classifiers we already have!



def boosted_ensemble(filename, learners, standard, verbose=False):
    data = orange.ExampleTable(filename)
    ensemble_learner = BoostOrangeLearner(learners, standard)

    if verbose:
        # Print the ensemble classifier that was trained on all of the
        # data.  For debugging the constituents of the ensemble classifier.
        classifier = ensemble_learner(data)
        print "ensemble classifier: %s" %(classifier)

    ensemble_crossval = orngTest.crossValidation([ensemble_learner], data,
                                                 folds=min(10,len(data)))
    accuracies = orngStat.CA(ensemble_crossval)
    brierscores= orngStat.BrierScore(ensemble_crossval)
    ROC_areas  = orngStat.AUC(ensemble_crossval)
    return accuracies[0], brierscores[0], ROC_areas[0]

DATASET_STANDARDS={
    "H004" : standardPartyClassifier,
    "H109" : standardPartyClassifier,
    "H110" : standardPartyClassifier,
    "S109" : standardPartyClassifier,
    "S110" : standardPartyClassifier,
    "vampires" : OrangeStandardClassifier("yes"),
    "titanic" : OrangeStandardClassifier("yes"),
    "breast-cancer" : OrangeStandardClassifier("recurrence-events"),
    "adult" : OrangeStandardClassifier(">50K") # this is big -- optional!
    }
"""
if __name__ == "__main__":
    dataset = "H004"

    describe_and_classify(dataset, learners)
    print "Boosting with our suite of orange classifiers:"
    print ("  accuracy: %.3f, brier: %.3f, auc: %.3f" %
           boosted_ensemble(dataset, learners, DATASET_STANDARDS[dataset]))

if __name__ == "__main__":
    dataset = "breast-cancer"
    describe_and_classify(dataset, learners)
    print "Boosting with our suite of orange classifiers:"
    print ("  accuracy: %.3f, brier: %.3f, auc: %.3f" %
           boosted_ensemble(dataset, learners, DATASET_STANDARDS[dataset]))
"""

# Play with the datasets mentioned above.  What ensemble of classifiers
# will give you the best cross-validation accuracy on the breast-cancer
# dataset?

def classifiers_ensemble(val):
    subset = {}
    for shortname in val:
        subset[shortname] = learners[shortname]
    accuracy, brier, auc = \
        boosted_ensemble("breast-cancer", subset,
                         DATASET_STANDARDS["breast-cancer"])
    #print "Accuracy with best classifiers: "+str(accuracy)
    return accuracy
if __name__ == "__main__":
    all_classifiers = ['maj', 'dt', 'knn', 'svml', 'svmp3', 'svmr', 'svms', 'nb']
    num_classify = len(all_classifiers)
    max_idx = num_classify - 1
    best = []
    best_prob = []
    best_so_far = []
    best_prob_so_far = 0.
    count = 0
    for num_include in range(1, 7):
        indices = range(num_include)
        go = True
        while go:
            if count % 20 == 0:
                print "Permutation %d" % count
            #print indices
            count += 1
            classifier = []
            for i in indices:
                classifier.append(all_classifiers[i])
            accuracy = classifiers_ensemble(classifier)
            if accuracy >= 0.74:
                print "Exceeds Expectations:"
                print "%s  :  %f" % (str(classifier), accuracy)
                best.append(classifier)
                best_prob.append(accuracy)
            if accuracy > best_prob_so_far:
                best_prob_so_far = accuracy
                best_so_far = classifier
                print "Best So Far:"
                print "%s  :  %f" % (str(classifier), accuracy)

            if indices[-1] == max_idx: #trigger a re-cycle
                go_inner = True
                point = len(indices) - 1
                while go_inner: # look for when you need to increment by 1
                    if point == 0:
                        go_inner = False
                        go = False
                    elif indices[point] == indices[point-1] + 1:# keep going
                        pass
                    else: # found the point
                        go_inner = False
                        indices[point-1] += 1
                        for shift_idx in range(point, len(indices)): # down shift
                            indices[shift_idx] = indices[shift_idx-1] + 1
                    point -= 1

            else: # simple case, just increment last
                indices[-1] += 1

            for index in indices:
                try:
                    assert index < num_classify
                except:
                    print indices
                    raise

    finfo = open("Best_ensembles.txt", "w")
    finfo.write("The Best So far: \n")
    finfo.write("%s  :  %f\n" % (best_so_far, best_prob_so_far))
    finfo.write("\n")
    finfo.write("All the good ensembles in no particular order:\n")
    for idx in range(len(best)):
        finfo.write("%s  :  %f\n" % (best[idx], best_prob[idx]))

    finfo.close()

classifiers_for_best_ensemble = ['nb']

## The standard survey questions.
HOW_MANY_HOURS_THIS_PSET_TOOK = None
WHAT_I_FOUND_INTERESTING = None
WHAT_I_FOUND_BORING = None


## The following code is used by the tester; please leave it in place!
def classifier_tester(classifier_name, data_set):
    """ Test a particular classifier, verify that it improves every step over 20 steps """
    return list(classifier_tester_helper(classifier_name, data_set))

def classifier_tester_helper(classifier_name, data_set):
    if classifier_name in globals():
        classifier = globals()[classifier_name]
        data = globals()[data_set]
        if isinstance(classifier, Classifier):
            original_classifier_count = len(classifier.classifiers)
            classifier.reset()
            for x in xrange(20):
                classifier.step()
                yield classifier.error_rate(data, standardPartyClassifier)

            classifier.reset()
            classifier.train(original_classifier_count)
            return
    raise Exception, "Error: Classifier %s doesn't exist!, can't test it" % classifier_name

from neural_net import *
def neural_net_tester(network_maker_func,
                      train_dataset_name,
                      test_dataset_name,
                      iterations):
    """Test a neural net making function on a named dataset"""
    neural_net.seed_random()
    network_maker_func = globals()[network_maker_func]
    train_dataset = globals()[train_dataset_name]
    test_dataset = globals()[test_dataset_name]
    nn = network_maker_func()

    train(nn, train_dataset, max_iterations=iterations)
    result = test(nn, test_dataset)
    return result

def neural_net_size_tester(network_maker_func):
    """Test a neural net size"""
    network_maker_func = globals()[network_maker_func]
    nn = network_maker_func()
    return len(nn.neurons)
