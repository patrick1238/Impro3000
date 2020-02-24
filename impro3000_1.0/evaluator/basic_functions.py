# -*- coding: utf-8 -*-
"""
Created on Fri May  3 11:29:04 2019

@author: patri
"""
import sys
sys.path.append("..")
import glob
import pandas as pd
import numpy as np

def collect_information(path,identifier):
    frame = pd.DataFrame()
    for filename in glob.iglob(path+'/**/*', recursive=True):
        if identifier in filename:
            if "csv" in filename:
                df = pd.read_csv(filename)
                frame = pd.concat([frame,df])
    if "Diagnose" in frame:
        frame.index = frame["Diagnose"]
        del frame["Diagnose"]
    return frame

def get_average(frame):
    values = {}
    for header in frame:
        values[header] = np.average(np.array(frame[header].tolist()))
    return values
                