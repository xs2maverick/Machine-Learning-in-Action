# =======================================================================
# @Author: Junbo Xin
# @Date: 2015/01/24
# @Description: basic function to be called by SVM
# =======================================================================

from numpy import *
import time
import matplotlib.pyplot as plt


# open a file: 1st and 2nd cols are features, 3rd col is label
def load_data_set(file_name):
    data_mat = []
    label_mat = []
    fr = open(file_name)
    for line in fr.readlines():
        line_arr = line.strip().split('\t')
        data_mat.append([float(line_arr[0]), float(line_arr[1])])
        label_mat.append(float(line_arr[2]))
    return data_mat, label_mat


# Giving the index of alpha: i. select one number(!=i) in (0, m)
def select_rand(i, m):
    j = i
    while j == i:
        j = int(random.uniform(0, m))
    return j


# make sure low <= aj <= high
def adjust_alpha(aj, high, low):
    if aj > high:
        aj = high
    if low > aj:
        aj = low
    return aj


# Implementation of basic SMO
# Giving training data: data_input and label_input, and parameter C, toler, max_iter
def smo_basic(data_input, label_input, C, toler, max_iter):
    start_time = time.time()
    # step 0: initialization for data and label, alpha initialized with 0
    data_mat = mat(data_input)
    label_mat = mat(label_input).transpose()
    b = 0.0
    m, n = shape(data_mat)
    alphas = mat(zeros((m, 1)))
    iter = 0
    while iter < max_iter:
        # step 1: select first alpha i
        alpha_pair_changed = 0
        for i in range(m):
            predict_i = float(multiply(alphas, label_mat).T * \
                             (data_mat * data_mat[i, :].T)) + b
            error_i = predict_i - float(label_mat[i])

            # step 2: checks if an example violates KKT conditions.
            if ((label_mat[i] * error_i < -toler) and (alphas[i] < C)) or \
               ((label_mat[i] * error_i > toler) and (alphas[i] > 0)):
                j = select_rand(i, m)   # randomly select the second alpha j
                predict_j = float(multiply(alphas, label_mat).T * \
                                 (data_mat * data_mat[j, :].T)) + b
                error_j = predict_j - float(label_mat[j])

                # step 4: allocate new memory for alpha i and j, in case override
                alpha_i_old = alphas[i].copy()
                alpha_j_old = alphas[j].copy()

                # step 5: make sure alpha value: 0 <= alpha[k] <=C, k = 1,2,...,m
                if label_mat[i] != label_mat[j]:   # y1 = 1, y2 = -1
                    Low = max(0, alphas[j]-alphas[i])
                    High = min(C, C+alphas[j]-alphas[i])
                else:   # y1 = y2 = 1
                    Low = max(0, alphas[j]+alphas[i]-C)
                    High = min(C, alphas[i]+alphas[j])
                if Low == High:
                    print 'Low==High'
                    continue

                # step 6: calculate eta = K11 + K22 - 2K12, make sure that eta > 0
                eta = data_mat[i, :]*data_mat[i, :].T + data_mat[j, :]*data_mat[j, :].T \
                      - 2.0*data_mat[i, :]*data_mat[j, :].T
                if eta <= 0:
                    print 'eta<=0'
                    continue

                # step 7: update the second alpha: j
                alphas[j] += label_mat[j] * (error_i-error_j)/eta
                alphas[j] = adjust_alpha(alphas[j], High, Low)
                if abs(alphas[j] - alpha_j_old) < 0.00001:
                    print 'j not moving enough'
                    continue

                # step 8: update the first alpha: i
                # aplha[1] = alpha[i]_old + y1*y2*(alpha[2]_old-alpha[2])
                alphas[i] += label_mat[j]*label_mat[i] * (alpha_j_old-alphas[j])
                b1 = b - error_i - label_mat[i]*(alphas[i]-alpha_i_old)* \
                     data_mat[i, :]*data_mat[i, :].T - label_mat[j]*(alphas[j]-alpha_j_old)* \
                     data_mat[i, :]*data_mat[j, :].T
                b2 = b - error_j - label_mat[i]*(alphas[i]-alpha_i_old)* \
                     data_mat[i, :]*data_mat[j, :].T - label_mat[j]*(alphas[j]-alpha_j_old)* \
                     data_mat[j, :]*data_mat[j, :].T

                # step 9: update b
                if (0 < alphas[i]) and (alphas[i] < C):
                    b = b1
                elif (0 < alphas[j]) and (alphas[j] < C):
                    b = b2
                else:
                    b = (b1+b2)/2.0
                alpha_pair_changed += 1
                print 'iter: %d i: %d, pairs changed %d' % (iter, i, alpha_pair_changed)

        # go out of the 'for, if alpha change, add the iter counts
        if alpha_pair_changed == 0:
            iter += 1
        else:
            iter = 0
        print 'iteration number: %d' % iter
    end_time = time.time()
    print 'Total Training time is: %fs' % (end_time - start_time)
    return b, alphas







