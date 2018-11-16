'''

'''

from lab3.ensemble import AdaBoostClassifier
from lab3.feature import NPDFeature

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import zero_one_loss
from sklearn.metrics import f1_score
from sklearn.metrics import classification_report

import numpy as np
import cv2

import os
import glob
import pickle
from datetime import datetime

dataset_dump_file = os.getcwd() + r'\dataset.pickle'
report_file = os.getcwd() + r'\report.txt'

def exp_loss(y_true, y_pred):
    '''calculate the exponential loss of groundtruth labels y_true and predictive labels y_pred

    :param y_true: an ndarray
    :param y_pred: an ndarray
    :return: the exponential loss
    '''
    if y_true.shape != y_pred.shape:
        raise Exception('The shape of y_true must be the same as y_pred')
    return np.exp(y_true * y_pred).sum()

def preprocess_imgs():
    '''load sample images, extract their NPD features and save the data into the local cache file 'dataset.pickle'
    '''

    def load_imgs(dataset_dir, label):
        img_paths = glob.glob(dataset_dir + r'\*')
        X = None
        for img_path in img_paths:
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, (24, 24))
            img_feat = NPDFeature(img).extract()

            if X is None:
                X = img_feat
            else:
                X = np.vstack((X, img_feat))

        y = np.array([label] * X.shape[0]).reshape(-1, 1)
        D = np.hstack((y, X))
        return D

    D_face = load_imgs(os.getcwd() + r'\datasets\original\face', 1)
    D_nonface = load_imgs(os.getcwd() + r'\datasets\original\nonface', -1)

    D = np.vstack((D_face, D_nonface))
    with open(dataset_dump_file, 'wb') as f:
        pickle.dump(D, f, pickle.HIGHEST_PROTOCOL)

def load_divide_dataset(test_size):
    with open(dataset_dump_file, 'rb') as f:
        D = pickle.load(f)

    D_train, D_val = train_test_split(D, test_size=test_size)
    y_train, X_train = D_train[:, 0:1], D_train[:, 1:]
    y_val, X_val = D_val[:, 0:1], D_val[:, 1:]

    return X_train, y_train, X_val, y_val

def face_classification_adaboost():

    def classified_result(y_train_true, y_train_pred, y_val_true, y_val_pred, report_title=''):

        train_loss_exp = exp_loss(y_train.flatten(), y_train_pred)
        train_loss_01 = zero_one_loss(y_train.flatten(), y_train_pred)

        val_loss_exp = exp_loss(y_val.flatten(), y_val_pred)
        val_loss_01 = zero_one_loss(y_val.flatten(), y_val_pred)

        report_str = '''{}
            train_loss_exp = {:.6f}
            train_loss_01  = {:.6f}

            val_loss_exp   = {:.6f}
            val_loss_01    = {:.6f}

            '''.format(report_title, train_loss_exp, train_loss_01, val_loss_exp, val_loss_01)

        with open(report_file, 'r+') as report_fp:
            report_fp.write(str(datetime.now()))
            report_fp.write(report_str)
            report_fp.write(classification_report(y_true=y_train, y_pred=y_train_pred,
                                                  target_names=class_name) + '\n')
            report_fp.write(classification_report(y_true=y_val, y_pred=y_val_pred,
                                                  target_names=class_name) + '\n\n')

    class_name = ['face', 'non-face']

    if dataset_dump_file not in glob.glob(os.getcwd() + r'\*'):
        preprocess_imgs()
    X_train, y_train, X_val, y_val = load_divide_dataset(test_size=0.25)

    X_train = X_train[0:1000, :]
    y_train = y_train[0:1000, :]

    # ------- A single weak classifier ------------

    weak_clf = DecisionTreeClassifier(max_depth=2)
    weak_clf.fit(X_train, y_train.flatten())

    y_train_pred = weak_clf.predict(X_train)
    y_val_pred = weak_clf.predict(X_val)

    classified_result(y_train, y_train_pred, y_val, y_val_pred, 'loss estimate of a single weak classifier (a sklearn.tree.DecisionTreeClassifier with max_depth = 2):')

    # ------- AdaBoost ------------

    n_weak_classifier = 10

    clf = AdaBoostClassifier(DecisionTreeClassifier, n_weak_classifier)
    clf.fit(X_train, y_train)

    y_train_pred = clf.predict(X_train)
    y_val_pred = clf.predict(X_val)

    classified_result(y_train, y_train_pred, y_val, y_val_pred, 'loss estimate of AdaBoost (base classifier: sklearn.tree.DecisionTreeClassifier with max_depth = 2):')

def test_sklearn_adaboostClf():
    pass

if __name__ == "__main__":
    # write your code here
    face_classification_adaboost()

    pass

