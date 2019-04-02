from Perceptron import BankNoteData
import numpy as np
import os
from scipy.optimize import minimize
from SVM import HW4p2
import matplotlib.pyplot as plt
from Perceptron import HW3p2
from Perceptron import Perceptron
from numpy import linalg as la


def hw4p3():
    redo_problem = True

    while redo_problem:

        problem = int(input("\nPlease choose a problem part\n1. "
                            "Problem 3a\n2. Problem 3b\n3. Problem 3c\n4. Exit\n"))

        valid_choice = True
        if problem != 1 and problem != 2 and problem != 3 and problem != 4:
            valid_choice = False

        while not valid_choice:
            print("Incorrect Choice")
            problem = int(input("\nPlease choose a problem part4\n1. "
                                "Problem 3a\n2. Problem 3b\n3. Problem 3c\n4. Exit\n"))

            if problem == 1 or problem == 2 or problem == 3 or problem == 4:
                valid_choice = True

        if problem == 1:
            choice_a(gamma=None, return_stats=False, use_kernel_prediction=False)
        elif problem == 2:
            choice_b()
        elif problem == 3:
            choice_c()
        else:
            break

        should_redo = str(input("\nWould you like to do another problem from HW 4 problem 3? y/n\n"))
        if should_redo == "n":
            redo_problem = False


def choice_a(gamma, return_stats, use_kernel_prediction):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data = BankNoteData.BankNoteData(dir_path + '/../Data/bank_note/train.csv')
    test_data = BankNoteData.BankNoteData(dir_path + '/../Data/bank_note/test.csv')

    C_values = np.array([100., 500., 700.])
    C_values = (1.0 / 873. * C_values).tolist()

    train_percentages_per_C = []
    test_percentages_per_C = []
    w_vectors = []
    alphas_by_C = []
    XXt = get_XXt(use_kernel_prediction, gamma, data)

    for C_value in C_values:
        a = np.zeros(data.features.shape[0])
        bounds = generate_bounds(a, C_value)
        cons = ({'type': 'eq', 'fun': a_dot_y, 'args': (data,)})

        res = minimize(svm, a, method='SLSQP', args=(data, XXt), jac=grad_svm,
                       tol=1e-3, bounds=bounds, constraints=cons)

        w_vector = np.zeros(data.features.shape[1])
        for i in range(0, data.features.shape[0]):
            w_vector += res.x[i] * data.output[i] * data.features[i, :]

        alphas_by_C.append(res.x)
        w_vectors.append(w_vector)
        print(w_vector)

        if use_kernel_prediction:
            train_percentage = get_percentages(data, data, res.x, gamma)
            test_percentage = get_percentages(test_data, data, res.x, gamma)
        else:
            train_percentage = HW3p2.get_percentages(w_vector, data, Perceptron.get_prediction)
            test_percentage = HW3p2.get_percentages(w_vector, test_data, Perceptron.get_prediction)
        train_percentages_per_C.append(train_percentage)
        test_percentages_per_C.append(test_percentage)

    train_percentages = np.array(train_percentages_per_C)
    test_percentages = np.array(test_percentages_per_C)

    if return_stats:
        return [train_percentages, test_percentages]
    else:
        print("Calculating results from first schedule")
        [w_vectors_from_a, train_pcts_from_a, test_pcts_from_a] = HW4p2.choice_a_or_b('a', print_progress=False,
                                                                                      num_reps=10, C_values=C_values)
        print("Calculating results from second schedule")
        [w_vectors_from_b, train_pcts_from_b, test_pcts_from_b] = HW4p2.choice_a_or_b('b', print_progress=False,
                                                                                      num_reps=10, C_values=C_values)
        norms = []
        abs_train_diffs = []
        abs_test_diffs = []
        for i in range(0, len(w_vectors_from_a)):
            norms.append(la.norm((w_vectors_from_a[i] / la.norm(w_vectors_from_a[i]))
                                 - (w_vectors[i] / la.norm(w_vectors[i]))))
            abs_train_diffs.append(np.abs(train_pcts_from_a[i] - train_percentages[i]))
            abs_test_diffs.append(np.abs(test_pcts_from_a[i] - test_percentages[i]))

        plt.plot(C_values, np.array(norms), C_values, np.array(abs_train_diffs), C_values, np.array(abs_test_diffs))
        plt.xlabel('C values')
        plt.ylabel('Errors')
        plt.legend(('Norm error', 'Train Error', 'Test Error'))
        plt.show()

        norms = []
        abs_train_diffs = []
        abs_test_diffs = []
        for i in range(0, len(w_vectors_from_a)):
            norms.append(la.norm((w_vectors_from_b[i] / la.norm(w_vectors_from_b[i]))
                                 - (w_vectors[i] / la.norm(w_vectors[i]))))
            abs_train_diffs.append(np.abs(train_pcts_from_b[i] - train_percentages[i]))
            abs_test_diffs.append(np.abs(test_pcts_from_b[i] - test_percentages[i]))

        plt.plot(C_values, np.array(norms), C_values, np.array(abs_train_diffs), C_values, np.array(abs_test_diffs))
        plt.xlabel('C values')
        plt.ylabel('Errors')
        plt.legend(('Norm error', 'Train Error', 'Test Error'))
        plt.show()


def choice_b():
    C_values = np.array([100., 500., 700.])
    C_values = (1.0 / 873. * C_values).tolist()
    gammas = [0.01, 0.1, 0.5, 1., 2., 5., 10., 100.]
    print("Running Kernel SVM")
    for gamma in gammas:
        print("Using gamma = %f:" % gamma)
        [train_pcts_by_gamma, test_pcts_by_gamma] = choice_a(gamma, True, use_kernel_prediction=True)
        for i, c_value in enumerate(C_values):
            print("For C value of %f we have the following errors" % c_value)
            print("Training error: %f" % train_pcts_by_gamma[i])
            print("Testing error: %f\n" % test_pcts_by_gamma[i])

    print("Running Linear SVM")
    [train_pcts, test_pcts] = choice_a(gamma=None, return_stats=True, use_kernel_prediction=False)
    for i, c_value in enumerate(C_values):
        print("For C value of %f we have the following errors" % c_value)
        print("Training error: %f" % train_pcts)
        print("Testing error: %f\n" % test_pcts)


def choice_c():
    return None


def svm(a, data, XXt):
    # _sum = 0.0
    # for i in range(0, data.features.shape[0]):
    #     for j in range(0, data.features.shape[0]):
    #         _sum += (data.features[i, :]).dot(data.features[j, :]) * data.output[i] * data.output[j] * a[i] * a[j]
    #
    # for i in range(0, data.features.shape[0]):
    #     _sum -= a[i]
    #
    # return 0.5 * _sum

    # Compact notation that may save computation time
    return 0.5 * np.matmul(np.multiply(a, data.output), np.matmul(XXt, np.multiply(a, data.output))) - np.sum(a)


def generate_bounds(a, C):
    bounds = []
    for i in range(0, a.shape[0]):
        bounds.append((0, C))

    return tuple(bounds)


def grad_svm(a, data, XXt):
    # grad = []
    # for i in range(0, a.shape[0]):
    #     _sum = 0.0
    #     for j in range(0, a.shape[0]):
    #         _sum += data.output[i] * data.output[j] * a[j] * (data.features[i, :].dot(data.features[j, :]))
    #
    #     _sum *= 0.5
    #     _sum += 0.5 * data.output[i] * data.output[i] * a[i] * (data.features[i, :].dot(data.features[i, :]))
    #     grad.append(_sum - 1.0)
    #
    # return np.array(grad)

    # Try compact notation
    return np.matmul(np.multiply(a, data.output), XXt) - np.ones(a.shape[0])


def a_dot_y(a, data):
    return a.dot(data.output)


def gaussian_kernel(x, y, gamma):
    return np.exp(-1.0 * (la.norm(x - y) ** 2) / gamma)


def get_kernel_prediction(alphas, x, gamma, data):
    _sum = 0.0
    for i in range(0, alphas.shape[0]):
        _sum += data.output[i] * alphas[i] * gaussian_kernel(data.features[i, :], x, gamma)
    return np.sign(_sum)


def get_percentages(test_data, data, alphas, gamma):
    num_correct = 0
    for row_ndx in range(0, test_data.features.shape[0]):
        if test_data.output[row_ndx] == get_kernel_prediction(alphas, data.features[row_ndx, :], gamma, data):
            num_correct += 1

    return 1.0 - float(num_correct / test_data.features.shape[0])


def get_XXt(use_kernel_prediction, gamma, data):
    if use_kernel_prediction:
        XXt = np.zeros(shape=(data.features.shape[0], data.features.shape[0]))
        for i in range(0, data.features.shape[0]):
            for j in range(i, data.features.shape[0]):
                XXt[i, j] = gaussian_kernel(data.features[i, :], data.features[j, :], gamma)

        for i in range(0, data.features.shape[0]):
            for j in range(0, i):
                XXt[i, j] = XXt[j, i]
    else:
        XXt = np.matmul(data.features, data.features.transpose())

    return XXt