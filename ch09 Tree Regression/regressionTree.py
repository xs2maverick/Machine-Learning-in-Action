# =============================================================================
# Author: Junbo Xin
# Date: 2015/02/07-10
# Description:  Regression Tree
# =============================================================================

from numpy import *


def load_data_set(file_name):
    num_feature = len(open(file_name).readline().split('\t'))-1
    data_mat = []
    fr = open(file_name).readlines()
    for line in fr:
        cur_line = line.strip().split('\t')
        float_line = map(float, cur_line)
        data_mat.append(float_line)
    return data_mat


# givint the data set and the feature(1-n) and the threshold value, split the data set in 2 parts
def bin_split_data(data_set, feature, value):
    # for a 2-d array A, nonzero(A) returns array(m,n), m is the rows, n is the cols
    mat0 = data_set[nonzero(data_set[:, feature] > value)[0], :][0]
    mat1 = data_set[nonzero(data_set[:, feature] <= value)[0], :][0]
    return mat0, mat1


def reg_leaf(data_set):
    return mean(data_set[:, -1])


def reg_error(data_set):
    return var(data_set[:, -1]) * shape(data_set)[0]


# select the best feature that has smallest error of the whole data set
def choose_best_split(data_set, leaf_type=reg_leaf, err_type=reg_error, ops=(1, 4)):
    max_err = ops[0]
    min_num = ops[1]
    # Stop condition 1: if there's 1 label, return
    if len(set(data_set[:, -1].T.tolist()[0])) == 1:
        return None, leaf_type(data_set)

    # step 1: preprocess the data
    m, n = shape(data_set)
    err_total = err_type(data_set)
    best_err = inf
    best_index = 0
    best_value = 0

    # step 2: go through each feature
    for feat_index in range(n-1):

        # step 3: for each feature, go through its all values
        for val in set(data_set[:, feat_index]):
            mat0, mat1 = bin_split_data(data_set, feat_index, val)
            if shape(mat0)[0] < min_num or shape(mat1)[0] < min_num:
                continue
            new_err = err_type(mat0) + err_type(mat1)

            # step 4: update the best feature if needed.
            if new_err < best_err:
                best_index = feat_index
                best_value = val
                best_err = new_err

    # Stop condition 2: current feature does not minimize error too much
    if err_total - best_err < max_err:
        return None, leaf_type(data_set)
    mat0, mat1 = bin_split_data(data_set, best_index, best_value)

    # Stop condition 3: current feature does not split the sample up to the minimal number
    if (shape(mat0)[0] < min_num) or (shape(mat1)[0] < min_num):
        return None, leaf_type(data_set)
    return best_index, best_value


def create_tree(data_set, leaf_type=reg_leaf, err_type=reg_error, ops=(1, 4)):
    # step 1: choose the best feature
    feat, val = choose_best_split(data_set, leaf_type, err_type, ops)
    if feat is None:
        return val
    ret_tree = {}
    ret_tree['split_index'] = feat   # which index to choose
    ret_tree['split_value'] = val

    # step 2: split the data into two parts
    left_set, right_set = bin_split_data(data_set, feat, val)

    # step 3: for the left and right data set, recursively call the create_tree
    ret_tree['left'] = create_tree(left_set, leaf_type, err_type, ops)
    ret_tree['right'] = create_tree(right_set, leaf_type, err_type, ops)

    return ret_tree


def plot_data_set(file_name):
    import matplotlib.pyplot as plt
    data_arr = load_data_set(file_name)
    n = shape(data_arr)[1]   # feature number of the data set
    x_arr = []
    y_arr = []
    for line in data_arr:
        line_arr = []
        for i in range(n-1):
            line_arr.append(line[i])
        x_arr.append(line_arr)
        y_arr.append(line[-1])

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(array(x_arr)[:, 0], array(mat(y_arr).T)[:, 0], c='blue')
    plt.show()


# judge whether obj is a tree or not
def is_tree(obj):
    return type(obj).__name__ == 'dict'


def get_mean(tree):
    if is_tree(tree['right']):
        tree['right'] = get_mean(tree['right'])
    if is_tree(tree['left']):
        tree['left'] = get_mean(tree['left'])
    return (tree['left'] + tree['right']) / 2.0


def prune(tree, test_data):
    # step 1: if test data is empty, return
    if shape(test_data) == 0:
        return get_mean(tree)

    # step 2: if test data is not empty, split it into 2 parts
    if is_tree(tree['right']) or is_tree(tree['left']):
        left_set, right_set = bin_split_data(test_data, tree['split_index'], tree['split_value'])
    if is_tree(tree['left']):
        tree['left'] = prune(tree['left'], left_set)
    if is_tree(tree['right']):
        tree['right'] = prune(tree['right'], right_set)

    # step 3: when left and right subtree is empty, calculate the error
    if not is_tree(tree['left']) and not is_tree(tree['right']):
        left_set, right_set = bin_split_data(test_data, tree['split_index'], tree['split_value'])
        err_not_merge = sum(power(left_set[:, -1] - tree['left'], 2)) + \
                        sum(power(right_set[:, -1] - tree['right'], 2))
        tree_mean = (tree['left'] + tree['right']) / 2.0
        err_merge = sum(power(test_data[:, -1] - tree_mean, 2))
        if err_merge < err_not_merge:
            print 'mergeing'
            return tree_mean
        else:
            return tree
    else:
        return tree