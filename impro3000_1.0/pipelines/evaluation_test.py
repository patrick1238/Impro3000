# -*- coding: utf-8 -*-
"""
Created on Wed May 29 14:47:37 2019

@author: patri
"""

import sys
sys.path.append("..")
import evaluator.basic_functions as bf
import networkx as nx
import matplotlib.pyplot as plt
plt.rcdefaults()
import matplotlib.pyplot as plt
import numpy as np

def main(config):
    values = bf.collect_information(config.get("output_path"),"cc")
    print(values)
    """
    for column in values:
        print(values[column])
    plt.rcdefaults()
    fig, ax = plt.subplots()
    x_pos = np.arange(len(binned))
    average = []
    standard_deviation = []
    for key in sorted(binned):
        array = np.array(binned[key]).astype(float)
        average.append(np.average(array))
        standard_deviation.append(np.std(array, dtype=np.float64,ddof=1))
    ax.bar(x_pos,average, yerr=standard_deviation, align='center',color='grey', ecolor='black')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(sorted(binned))
    fig.savefig(arguments["results"]+"binned_cc_per_degree_bar.tif",dpi=400)
    plt.close()
    """
    