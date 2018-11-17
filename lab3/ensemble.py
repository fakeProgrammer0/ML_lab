'''A simple AdaBoostClassifier
contract changed explaination: to allow client of the AdaBoostClassifier to set parameters of the weak_classifier, the param {weak_classifier} of the constructor is designed as a class instance instead of a class object.
接口改动说明：为了让AdaBoostClassifier的客户能够设置弱分类器的参数，这里把构造函数的{weak_classifier}参数设置为弱分类器的[实例]，而不是弱分类器的[类对象]
'''

import math
import pickle
import numpy as np
import copy

import os
from lab3.ML_toolkit import sign_helper
from lab3.ML_toolkit import exp_loss
from sklearn.metrics import zero_one_loss
import matplotlib.pyplot as plt

class AdaBoostClassifier:
    '''A simple AdaBoost Classifier.
    Only support binary classification in which the label y is from {-1, +1} currently.
    '''

    def __init__(self, weak_classifier, n_weakers_limit):
        '''Initialize AdaBoostClassifier

        Args:
            weak_classifier: A instance of weak classifier, which is recommend to be sklearn.tree.DecisionTreeClassifier.
            n_weakers_limit: The maximum number of weak classifier the model can use.
        '''
        self.weak_clf = weak_classifier
        self.n_weakers_limit = n_weakers_limit

    def is_good_enough(self):
        '''Optional'''
        pass

    def fit(self,X,y):
        '''Build a boosted classifier from the training set (X, y).

        Args:
            X: An ndarray indicating the samples to be trained, which shape should be (n_samples,n_features).
            y: An ndarray indicating the ground-truth labels correspond to X, which shape should be (n_samples,1),
               where the class label y[i, 0] is from {-1, +1}.
        '''
        w = np.ones(y.shape)
        w = w / w.sum() # regularization

        self.a = []
        self.base_clfs = []

        for i in range(self.n_weakers_limit):
            base_clf = copy.copy(self.weak_clf)
            base_clf.fit(X, y.flatten(), w.flatten())

            y_pred = base_clf.predict(X).reshape((-1, 1))

            err_rate = w.T.dot(y_pred != y)[0][0] / w.sum()

            if err_rate > 1 / 2 or err_rate == 0.0:
                break

            weight_param_a = math.log((1 - err_rate) / err_rate) / 2

            self.base_clfs.append(base_clf)
            self.a.append(weight_param_a)

            w = w * np.exp(-weight_param_a * y * y_pred)
            w = w / w.sum() # regularization

            # prevent overfiting
            # if self.is_good_enough():
            #     break;


    def predict_scores(self, X):
        '''Calculate the weighted sum score of the whole base classifiers for given samples.

        Args:
            X: An ndarray indicating the samples to be predicted, which shape should be (n_samples,n_features).

        Returns:
            An one-dimension ndarray indicating the scores of differnt samples, which shape should be (n_samples,1).
        '''
        y_score_pred = np.zeros((X.shape[0], 1))
        for i, clf in enumerate(self.base_clfs):
            y_score_pred += self.a[i] * clf.predict(X).reshape((-1, 1))

        return y_score_pred

    def predict(self, X, threshold=0):
        '''Predict the catagories for given samples.

        Args:
            X: An ndarray indicating the samples to be predicted, which shape should be (n_samples,n_features).
            threshold: The demarcation number of deviding the samples into two parts.

        Returns:
            An ndarray consists of predicted labels, which shape should be (n_samples,1).
        '''
        return sign_helper(self.predict_scores(X), threshold=threshold)

    @staticmethod
    def save(model, filename):
        with open(filename, "wb") as f:
            pickle.dump(model, f)

    @staticmethod
    def load(filename):
        with open(filename, "rb") as f:
            return pickle.load(f)

    def loss_estimate(self, X_train, y_train, X_val, y_val):
        '''Estimate training loss of AdaBoost

        Args:
            X_train, X_val: ndarrays indicating the samples to be trained / validated, which shape should be (n_samples,n_features).
            y_train, y_val: ndarrays indicating the ground-truth labels correspond to X_train / X_val, which shape should be (n_samples,1), where the class label y[i, 0] is from {-1, +1}.
        '''
        w = np.ones(y_train.shape)
        w = w / w.sum()  # regularization

        self.a = []
        self.base_clfs = []

        train_losses_01, val_losses_01 = [], []
        train_losses_exp, val_losses_exp = [], []

        for i in range(self.n_weakers_limit):
            base_clf = copy.copy(self.weak_clf)
            base_clf.fit(X_train, y_train.flatten(), w.flatten())

            # train_pred generated by the current base classifier
            y_train_pred_curr = base_clf.predict(X_train).reshape((-1, 1))

            err_rate = w.T.dot(y_train_pred_curr != y_train)[0][0] / w.sum()

            if err_rate > 1 / 2 or err_rate == 0.0:
                break

            weight_param_a = math.log((1 - err_rate) / err_rate) / 2

            self.base_clfs.append(base_clf)
            self.a.append(weight_param_a)

            w = w * np.exp(-weight_param_a * y_train * y_train_pred_curr)
            w = w / w.sum()  # regularization

            # prevent overfiting
            # if self.is_good_enough():
            #     break;

            # ----- loss estimate -----
            y_train_pred = self.predict(X_train)
            y_val_pred = self.predict(X_val)

            train_loss_01 = zero_one_loss(y_true=y_train.flatten(), y_pred=y_train_pred.flatten())
            train_loss_exp = exp_loss(y_true=y_train.flatten(), y_pred=y_train_pred.flatten())
            train_losses_01.append(train_loss_01)
            train_losses_exp.append(train_loss_exp)

            val_loss_01 = zero_one_loss(y_true=y_val.flatten(), y_pred=y_val_pred.flatten())
            val_loss_exp = exp_loss(y_true=y_val.flatten(), y_pred=y_val_pred.flatten())
            val_losses_01.append(val_loss_01)
            val_losses_exp.append(val_loss_exp)

        plt.figure(figsize=(16, 9))
        plt.plot(train_losses_01, '-', color='r', label='train_losses_01')
        plt.plot(val_losses_01, '--', color='k', label='val_losses_01')
        plt.xlabel('epoch')
        plt.ylabel('loss')
        plt.title('01 loss estimate during AdaBoost training')
        plt.legend()
        plt.savefig(os.getcwd() + r'\AdaBoost_losses_01.png')
        plt.show()

        plt.figure(figsize=(16, 9))
        plt.plot(train_losses_exp, '-', color='m', label='train_losses_exp')
        plt.plot(val_losses_exp, '--', color='y', label='val_losses_exp')
        plt.xlabel('epoch')
        plt.ylabel('loss')
        plt.title('exp loss estimate during AdaBoost training')
        plt.legend()
        plt.savefig(os.getcwd() + r'\AdaBoost_losses_exp.png')
        plt.show()



