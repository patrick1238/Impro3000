# -*- coding: utf-8 -*-
"""
Created on Tue Dec 11 14:40:06 2018

@author: patri
"""

class feature_set:
    
    __cellGraph = None
    __feature_set = {}
    
    def __init__(self,cellGraph = None):
        self.__cellGraph = cellGraph
        
    def set_graph(self,cellGraph):
        self.__cellGraph = cellGraph
    
    def add_feature(self,key,value):
        self.__feature_set[key] = value
        
    def get_feature(self,key):
        return self.__feature_set[key]
    
    def print_features(self):
        output_string = "Properties of Graph " + self.__cellGraph.get_identifier() + "\n"
        for key in self.__feature_set:
            output_string = output_string + key + ": " + str(self.__feature_set[key]) + "\n"
        print(output_string)
        
    def save_as_impro_properties_file(self,path):
        output_file =  open(path + self.__cellGraph.get_identifier() + "_graphproperties.iaf", "w")
        output_file.write(self.__create_output_string())
        output_file.close()
            
        
    def __create_output_string(self):
        header = "origin"
        values = self.__cellGraph.get_identifier()
        for key in self.__feature_set:
            header = header + "," + key
            values = values + "," + str(self.__feature_set[key])
        return header + "\n" + values