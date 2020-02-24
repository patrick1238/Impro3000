# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 14:06:32 2019

@author: patri
"""

import pandas as pd
import numpy as np

def convert_featureset_to_pandasdf_outdated(feature_set):
    converter_dict = {}
    for feature in feature_set:
        runner = 0
        disease_list = []
        value_list = []
        id_list = []
        for disease in feature[1]:
            for value in feature[1][disease]:
                id_list.append(runner)
                disease_list.append(disease)
                value_list.append(value)
                runner = runner + 1
        converter_dict["diagnose"] = pd.Series(disease_list,index=id_list)
        converter_dict[feature[0]] = pd.Series(value_list,index=id_list)
    df = pd.DataFrame(converter_dict)
    return df

def convert_featureset_to_pandasdf(feature_set):
    first_key = list(feature_set.keys())[0]
    header = list(feature_set[first_key].keys())
    df = pd.DataFrame(columns=header)
    for case in feature_set:
        df.loc[case] = list(feature_set[case].values())
    return df