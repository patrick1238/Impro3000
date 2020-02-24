# -*- coding: utf-8 -*-
"""
Created on Fri May  3 11:29:34 2019

@author: patri
"""
import pandas as pd
def csv_to_dataframe(path):
    df = pd.DataFrame.from_csv(path)
    return df