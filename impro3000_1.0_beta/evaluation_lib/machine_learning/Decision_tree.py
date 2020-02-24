# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 13:39:31 2019

@author: patri
"""
import sys
sys.path.append("../..")
import evaluation_lib.machine_learning.basic_functions as bf
from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import pandas as pd
from graphviz import Source
import numpy as np
import random
import pickle
#from subprocess import call

colums_to_drop = ["Average_EulerNumber","Average_CellClass","Average_Compactness",
                  "Average_Eccentricity","Average_Extent","Average_MaxFeretDiameter",
                  "Average_MaximumRadius","Average_MeanRadius","Average_MedianRadius",
                  "Average_MinFeretDiameter","Average_MinorAxisLength",
                  "Average_Orientation","Average_clustering_coefficient",
                  "Average_MajorAxisLength","Average_Perimeter",
                  "Number_connected_components","Number_of_edges",
                  "Density"]

class Decision_tree():
    
    __dataframe = None
    __model = None
    
    def __init__(self, value_dict=None):
        print(value_dict)
        if value_dict is not None:
            self.__dataframe = bf.convert_featureset_to_pandasdf(value_dict)
        else:
            self.__model = pickle.load("../evaluation_lib/machine_learning/decision_tree.p","rb")
    
    def train(self,key):
        test = colums_to_drop
        test.append(key)
        X = self.__dataframe.drop(test, axis=1)
        Y = self.__dataframe[key]
        test2 = []
        x = random.randint(1,100)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y,test_size=0.25, random_state=x)
        self.__model = tree.DecisionTreeClassifier()
        self.__model.fit(X, Y)
        Y_predict = self.__model.predict(X_test)
        score = accuracy_score(Y_test, Y_predict)
        test2.append(score)
        df = pd.DataFrame(
                confusion_matrix(Y_test, Y_predict),
                columns=['Predicted LAD', 'Predicted Mixed', 'Predicted NS'],
                index=['True LAD', 'True Mixed', 'True NS']
                )
        print(df)
        tree.export_graphviz(self.__model, out_file="tree.dot", feature_names=X.columns)
        #s = pickle.dump(self.__model, open("../evaluation_lib/machine_learning/decision_tree.p","wb"))
        """
        graph = Source(tree.export_graphviz(model, out_file="tree.png", feature_names=X.columns))
        png_bytes = graph.pipe(format='png')
            with open('dtree_pipe.png','wb') as f:
            f.write(png_bytes)
        #call(['dot', '-T', 'png', 'tree.dot', '-o', 'tree.png'])
        """