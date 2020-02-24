# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 17:42:09 2019

@author: patri
"""

import matplotlib.pyplot as plt
plt.rcdefaults()
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab
import math
import scipy.stats as st
from pathlib import Path
import os

line_style = ["-","--","-.",":"]

def __observe_path_for_existence(path):
    file = Path(path)
    if not file.is_dir():
        os.makedirs(path)
    return path

def multi_normal_distribution(feature,feature_dictionary,output_path,xlabel="",ylabel="",title=""):

    legend = []
    fig, ax = plt.subplots()
    counter = 0
    for key in feature_dictionary:
        legend.append(key)
        array = np.array(feature_dictionary[key]).astype(float)
        mu = np.average(array)
        sigma = np.std(array, dtype=np.float64,ddof=1)
        x = np.linspace(mu - 3*sigma, mu + 3*sigma, 100)
        ax.plot(x,st.norm.pdf(x, mu, sigma),line_style[counter], linewidth=2,color="grey")
        counter = counter + 1
    plt.legend(legend, loc='upper left')
    plt.xlabel(xlabel,fontname="Arial")
    plt.ylabel(ylabel,fontname="Arial")
    plt.title(feature,fontname="Arial")
    plt.savefig(output_path+feature+"_normal_distribution.tif")#,dpi=1200)
    plt.close()
    
def multi_bar(feature,feature_dictionary,output_path,xlabel="",ylabel="",title=""):

    plt.rcdefaults()
    fig, ax = plt.subplots()
    x_pos = np.arange(len(feature_dictionary))
    average = []
    standard_deviation = []
    for cur in feature_dictionary.values():
        array = np.array(cur).astype(float)
        average.append(np.average(array))
        standard_deviation.append(np.std(array, dtype=np.float64,ddof=1))
    ax.bar(x_pos,average, yerr=standard_deviation, align='center',color='grey', ecolor='black')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(feature_dictionary.keys())
    ax.set_title(feature)
    plt.xlabel(xlabel,fontname="Arial")
    plt.ylabel(ylabel,fontname="Arial")
    plt.title(feature,fontname="Arial")
    fig.savefig(output_path+feature+"_bar.tif")#,dpi=1200)
    plt.close()