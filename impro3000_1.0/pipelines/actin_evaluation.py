# -*- coding: utf-8 -*-
"""
Created on Fri May  3 11:28:22 2019

@author: patri
"""

import sys
sys.path.append("..")
from evaluator import evaluator

def main(config):
    values = evaluator.collect_information(config.get("output_path"),"validation_results")
    average_values = evaluator.get_average(values)
    output = "On average:\n"
    for key in average_values:
        output = output + key + ": " + str(average_values[key]) + "\n"
    print(output)