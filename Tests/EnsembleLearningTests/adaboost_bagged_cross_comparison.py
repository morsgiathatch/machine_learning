from Data.bank import BankData
from EnsembleLearning import BaggingTrees
from DecisionTree import Id3
import numpy as np
import sys
import os
import random


def adaboost_bagged_cross_comparison():
    # Train data
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data = BankData.Data()
    data.initialize_data_from_file(dir_path + '/../../Data/bank/train.csv', False)

    # Test data
    test_data = BankData.Data()
    test_data.initialize_data_from_file(dir_path + '/../../Data/bank/test.csv', False)

    bagged_trees = []
    full_trees = []

    factor = float(input("Please enter a number to get fraction of features. (e.g., `2` uses 1/2 of features):\n"))

    counter = 1
    toolbar_width = 100
    print("Building trees")
    sys.stdout.write("Progress: [%s]" % (" " * toolbar_width))
    sys.stdout.flush()

    for i in range(0, 100):
        # sample 100 features uniformly without replacement
        examples = get_samples(data)
        forest = BaggingTrees.BaggingTrees(t_value=100, features=examples, attributes=data.attributes,
                                           attribute_factor=factor)
        forest.fit(print_status_bar=False)
        bagged_trees.append(forest)
        id3 = Id3.Id3(metric='information_gain')
        full_trees.append(id3.fit(examples, data.attributes, None, data.labels, 0, float("inf")))
        sys.stdout.write('\r')
        sys.stdout.flush()
        sys.stdout.write('Progress: [%s' % ('#' * counter))
        sys.stdout.write('%s]' % (' ' * (toolbar_width - counter)))
        sys.stdout.flush()
        counter += 1

    print("\nCalculating squared mean error of full trees.")
    full_trees_results = get_squared_mean_error_np(data, full_trees, False)
    print("\nMean Squared Error for the full trees is: " + "%.16f" % (full_trees_results[0] + full_trees_results[1]))
    print("Bias was %s, Variance was %s" % (full_trees_results[0], full_trees_results[1]))
    print("Calculating squared mean error for bagged trees.")
    bagged_trees_results = get_squared_mean_error_np(data, bagged_trees, True)
    print("\nMean Squared Error for the bagged trees is: " + "%.16f"
          % (bagged_trees_results[0] + bagged_trees_results[1]))
    print("Bias was %s, Variance was %s" % (bagged_trees_results[0], bagged_trees_results[1]))


def get_samples(data):

    examples = []
    indices = random.sample(range(0, len(data.examples)), 1000)
    for ndx in indices:
        examples.append(data.examples[ndx])

    return examples


def get_squared_mean_error_np(data, trees, bagged_trees):
    bias = 0.0
    variance = 0.0
    toolbar_width = 100
    sys.stdout.flush()
    sys.stdout.write("Progress: [%s]" % (" " * toolbar_width))
    sys.stdout.flush()

    counter = 1
    subdivision = int(len(data.examples) / 100)

    results = np.empty([len(data.examples), len(trees)])
    if bagged_trees:
        for i, example in enumerate(data.examples):
            for j, tree_set in enumerate(trees):
                results[i, j] = tree_set.predict(example)

            counter += 1
            if counter % subdivision == 0:
                sys.stdout.write('\r')
                sys.stdout.flush()
                sys.stdout.write('Progress: [%s' % ('#' * (int(counter / subdivision))))
                sys.stdout.write('%s]' % (' ' * (toolbar_width - int(counter / subdivision))))
                sys.stdout.flush()
    else:
        for i, example in enumerate(data.examples):
            for j, tree in enumerate(trees):
                results[i, j] = tree.predict(example)

            counter += 1
            if counter % subdivision == 0:
                sys.stdout.write('\r')
                sys.stdout.flush()
                sys.stdout.write('Progress: [%s' % ('#' * (int(counter / subdivision))))
                sys.stdout.write('%s]' % (' ' * (toolbar_width - int(counter / subdivision))))
                sys.stdout.flush()

    for i, example in enumerate(data.examples):
        tree_avg = np.sum(results[i, :]) / float(len(trees))
        bias += np.power(example.get_label() - tree_avg, 2.0)
        diff = results[i, :] - tree_avg
        variance += np.dot(diff, diff) / (float(len(trees)) - 1.0)

    sys.stdout.write('\n')
    sys.stdout.flush()
    bias /= float(len(data.examples))
    variance /= float(len(data.examples))
    return [bias, variance]
