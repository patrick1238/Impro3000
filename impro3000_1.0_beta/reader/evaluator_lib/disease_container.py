# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 11:35:51 2019

@author: patri
"""

class disease_container():
    
    feature_set = None
    case_ids = None
    
    def __init__(self,disease=None):
        self.feature_set = {}
        self.case_ids = []
        
    def add_case(self,case_id,path):
        self.case_ids.append(case_id)
        self.__read_result_file(path)
    
    def __read_result_file(self,path):
        result_file = open(path)
        header = result_file.readline().strip("\n").split(",")
        results = result_file.readline().strip("\n").split(",")
        for i in range(len(header)):
            if header[i] in self.feature_set:
                self.feature_set[header[i]].append(results[i])
            else:
                self.feature_set[header[i]] = [results[i]]
                
    def get_feature_names(self):
        return self.feature_set.keys()
    
    def get(self,feature):
        return self.feature_set[feature]