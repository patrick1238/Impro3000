# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 14:31:35 2020

@author: patri
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 11:08:54 2019

@author: patri
"""

import argparse as ap

class Config():
    
    config = None
    
    def __init__(self,config_name="3DConfig",parse_cmd=True):
        self.config = {}
        self.read_config("Config/"+config_name+".txt")
        if parse_cmd:
            self.parse_commandline_input()
        
    def get(self,key):
        if key in self.config:
            return self.config[key]
        else:
            return "unknown"
    
    def set_value(self,key,value):
        self.config[key] = value
        
    def read_config(self,config_path):
        config_file = open(config_path,"r")
        for line in config_file:
            if "#" not in line and len(line) > 1:
                splitted = line.split("=")
                self.config[splitted[0]] = splitted[1].strip("\n")
        config_file.close()
        
    def parse_commandline_input(self):
        parser = ap.ArgumentParser()
        
        	# specify the layer to be read:
        parser.add_argument("-c", "--channel", help="enter number of desired layer here", default=0)
        	
        