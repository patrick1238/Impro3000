# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 14:37:54 2019

@author: patri
"""
import numpy as np

def get_average(frame):
    values = {}
    for header in frame:
        values[header] = np.average(np.array(frame[header].tolist()))
    return values