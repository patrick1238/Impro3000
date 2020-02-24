# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 15:03:47 2019

@author: patri
"""
import sys
sys.path.append("..")
import evaluation_lib.machine_learning.Decision_tree as dt

def main(feature_set,output_folder):
    print(feature_set)
    tree = dt.Decision_tree(feature_set)
    tree.train("disease")