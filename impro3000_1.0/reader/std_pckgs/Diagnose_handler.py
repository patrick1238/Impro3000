# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 16:14:54 2019

@author: patri
"""

class Diagnose_handler():
    
    Diagnose_handler = None
    
    def __init__(self,diagnose_file="Diagnose"):
        self.Diagnose_handler = {}
        self.read_diagnose_file("files/"+diagnose_file+".csv")
        
    def get(self,key):
        if key in self.Diagnose_handler:
            return self.Diagnose_handler[key]
        else:
            return "unknown"
    
    def set_value(self,key,value):
        self.Diagnose_handler[key] = value
        
    def read_diagnose_file(self,diagnose_path):
        diagnose_file = open(diagnose_path,"r")
        for line in diagnose_file:
            if "#" not in line and len(line) > 1:
                splitted = line.split(",")
                self.Diagnose_handler[splitted[0]] = splitted[1].strip("\n")
        diagnose_file.close()