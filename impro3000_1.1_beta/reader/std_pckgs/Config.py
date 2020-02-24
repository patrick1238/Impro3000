# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 11:08:54 2019

@author: patri
"""

import argparse as ap

class Config():
    
    config = None
    
    def __init__(self,config_name="WSI_Reader_Config",parse_cmd=True):
        self.config = {}
        self.read_config("local_files/"+config_name+".txt")
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
        parser.add_argument("-l", "--layer", help="enter number of desired layer here", default=0)
        	
        # set the -gfi tag if no tiling is requiered. the image will be read into one image object. consider RAM availibility when opening big images with this option
        parser.add_argument("-gfi", "--get_full_image", help="set if no tiling is required", default=False, action='store_true')
        
        	# set the -gfi tag if no tiling is requiered. the image will be read into one image object. consider RAM availibility when opening big i default=True, action='store_false'mages with this option
        parser.add_argument("-i", "--input_path", help="enter the desired input path, single image or folder",default="None")
        
        	# set the -gfi tag if no tiling is requiered. the image will be read into one image object. consider RAM availibility when opening big images with this option
        parser.add_argument("-o", "--output_path", help="enter the desired output path", default="None")
        
        	# path to the pipeline script:
        parser.add_argument("-prepipe", "--preprocessing_pipeline", help="enter the path to your pipeline script, including the pipeline name", type=str, default="None")
        
        	# path to the pipeline script:
        parser.add_argument("-postpipe", "--postprocessing_pipeline", help="enter the path to your postprocessing pipeline script, including the pipeline name", type=str, default="None")
        
        parser.add_argument("-evalpipe", "--evaluation_pipeline", help="enter the path to your evaluation pipeline script, including the pipeline name", type=str, default="None")	
		
        	# option to set primary staining
        parser.add_argument("-s", "--staining", help="enter the staining of the image", type=str, default="None")
                
        	# list with all parsed cammand line inputs:
        args = parser.parse_args()
        for key,value in vars(args).items():
            if value != "None":
                self.config[key] = value