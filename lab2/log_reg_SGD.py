# train_dataset_url = '../dataset/a9a.txt'
# val_dataset_url = '../dataset/a9a_t.txt'
train_dataset_url = r'D:\MyData\Temp Codes\Github\ML_labs\dataset\a9a.txt'
val_dataset_url = r'D:\MyData\Temp Codes\Github\ML_labs\dataset\a9a_t.txt'

n_features = 123

# --------------------------

import numpy as np
import math
import matplotlib.pyplot as plt
import random

from sklearn.datasets import load_svmlight_file

def preprocess(dataset_url, n_features):
    X, y = load_svmlight_file(dataset_url, n_features=n_features)
    y = y.reshape(-1, 1)
    X = X.toarray()
    X = np.hstack((np.ones(y.shape), X))
    return X, y

# TODO: use matrix operations to substitute loops
def log_reg_MLE_MSGD(X_train, y_train, X_val, y_val, batch_size=100, max_epoch=200, learning_rate=0.001, reg_param=0.3):
    '''logistic regression using mini-batch stochastic gradient descent with maximum likelihood method
    :param X_train: train data, a (n_samples, n_features + 1) ndarray, where the 1st column are all ones, ie.numpy.ones(n_samples)
    :param y_train: labels, a (n_samples, 1) ndarray
    :param X_val: validation data
    :param y_val: validation labels
    :param max_epoch: the max epoch for training
    :param learning_rate: the hyper parameter to control the velocity of gradient descent process, also called step_size
    :param reg_param: the L2 regular term factor for the objective function

    :return w: the weight vector, a (n_features + 1, 1) ndarray
    :return log_LEs_train: the min log likelihood estimate of the training set during each epoch
    :return log_LEs_val: the min log likelihood estimate of the validation set during each epoch
    '''
    n_train_samples, n_features = X_train.shape
    if n_train_samples < batch_size:
        batch_size = n_train_samples

    # for calculation convenience, y is represented as a row vector
    y_train = y_train.reshape(1, -1)[0, :]
    y_val = y_val.reshape(1, -1)[0, :]

    # init weight vectors
    # for calculation convenience, w is represented as a row vector
    w = np.zeros(n_features)

    log_LEs_train = []
    log_LEs_val = []

    for epoch in range(0, max_epoch):

        temp_sum = np.zeros(w.shape)
        batch_indice = random.sample(range(0, n_train_samples), batch_size)

        for idx in batch_indice:
            exp_term = math.exp(-y_train[idx] * np.dot(X_train[idx], w))
            temp_sum += y_train[idx] * X_train[idx] * exp_term / (1 + exp_term)

        # update w using gradient of the objective function
        w = (1 - learning_rate * reg_param) * w + learning_rate / batch_size * temp_sum

        log_LE_train = min_log_LE(X_train, y_train, w)
        log_LEs_train.append(log_LE_train)
        log_LE_val = min_log_LE(X_val, y_val, w)
        log_LEs_val.append(log_LE_val)
        print("epoch {:3d}: loss_train = [{:.6f}]; loss_val = [{:.6f}]".format(epoch, log_LE_train, log_LE_val))

    return w, log_LEs_train, log_LEs_val

def min_log_LE(X, y, w):
    '''The min log likelihood estimate
    :param X: the data, a (n_samples, n_features) ndarray
    :param y: the groundtruth labels, required in a row shape
    :param w: the weight vector, required in a row shape
    '''
    n_samples = X.shape[0]
    loss_sum = 0
    for i in range(0, n_samples):
        loss_sum += np.log(1 + np.exp(-y[i] * (np.dot(X[i], w))))

    return loss_sum / n_samples

def logistic_g(Z):
    return 1 / (1 + math.exp(-Z))

def threshold_loss(X, y, w, threshold=0.5):
    n_samples = X.shape[0]
    y_predict = np.dot(X, w)
    for i in range(0, n_samples):
        if logistic_g(y_predict[i]) > threshold:
            y_predict[i] = +1
        else:
            y_predict[i] = -1

    # 这样的损失函数怪怪的
    return np.average(np.abs(y_predict - y))

def threshold_Ein(X, y, w, threshold=0.5):
    n_samples = X.shape[0]

    y_predict = np.dot(X, w)
    for i in range(0, n_samples):
        if logistic_g(y_predict[i]) > threshold:
            y_predict[i] = +1
        else:
            y_predict[i] = -1

    loss_sum = 0
    for i in range(0, n_samples):
        loss_sum += math.log(1 + np.exp(-y[i] * y_predict[i]))

    return loss_sum / n_samples

def loss_Ein2(X, y, w):
    '''
    :param X: the data, a m*d ndarray
    :param y: the groundtruth labels, a m*1 ndarray
    :param w: the weight vector, a d*1 ndarray
    :return:
    '''
    return np.average(np.log(np.ones(y.shape) + np.exp(y * np.dot(X, w))))

def run_log_reg2():
    global n_features
    X_train, y_train = preprocess(dataset_url=train_dataset_url, n_features=n_features)
    X_val, y_val = preprocess(dataset_url=val_dataset_url, n_features=n_features)
    w, losses_train, losses_val = log_reg_MLE_MSGD(X_train, y_train, X_val, y_val, batch_size=512, max_epoch=200, learning_rate=0.1, reg_param=0.1)

    plt.figure(figsize=(16,9))
    plt.plot(losses_train, "-", color="r", label="train loss")
    plt.plot(losses_val, "-", color='b', label='val loss')
    plt.xlabel('epoch')
    plt.ylabel('loss')
    plt.legend()
    plt.title('loss graph')
    plt.show()

if __name__ == "__main__":
    # run_SGD()
    run_log_reg2()
