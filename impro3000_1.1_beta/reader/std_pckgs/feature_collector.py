# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 13:11:00 2019

@author: patri
"""

import sys
sys.path.append("..")
import glob
import pandas as pd
import os

extensions = ["icf","iaf","iif"]

def collect_information(folder):
    frames = {}
    for extension in extensions:
        frames[extension] = pd.DataFrame()
    for filename in glob.iglob(folder+'/**/*', recursive=True):
        if not os.path.isdir(filename):
            extension = filename.split(".")[1]
            if extension in extensions:
                df = pd.read_csv(filename)
                frames[extension] = pd.concat([frames[extension],df])
    print(frames)
    return frames["icf"],frames["iaf"],frames["iif"]             