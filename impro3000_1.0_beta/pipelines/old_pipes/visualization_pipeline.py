# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 15:03:47 2019

@author: patri
"""
import sys
sys.path.append("..")
import evaluation_lib.visualization.plot3000 as plotter

def main(feature_set,output_folder):
    print("visualizing feature_set")
    for feature in feature_set:
        #plotter.multi_normal_distribution(feature[0],feature[1],output_folder)
        #plotter.multi_bar(feature[0],feature[1],output_folder)
        plotter.multi_boxplot_with_scatters(feature[0],feature[1],output_folder)