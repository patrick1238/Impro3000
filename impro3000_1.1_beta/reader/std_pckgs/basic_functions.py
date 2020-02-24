# -*- coding: utf-8 -*-
"""
Created on Thu May 23 17:36:27 2019

@author: patri
"""
import sys
sys.path.append("..")
from pathlib import Path
import importlib
import inspect
import os
import shutil
from datetime import datetime

def identify_main(pipe):
    spec = importlib.util.spec_from_file_location("pipeline", os.path.abspath("../pipelines/"+pipe+".py"))
    pipeline = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = pipeline
    spec.loader.exec_module(pipeline)
    functionList = inspect.getmembers(pipeline,inspect.isfunction)
    for function in functionList:
        if function[0] == "main":
            return function[1]
        
def delete_folder(path):
    shutil.rmtree(path)
        
def observe_path_for_existence(path):
    file = Path(path)
    if not file.is_dir():
        os.makedirs(path)
    return path

def prepare_batch_workspace(config):
    timestamp = str(datetime.now()).replace(":","-").replace(" ","_")
    config.set_value("batch_results", observe_path_for_existence(config.get("output_path") + timestamp[:timestamp.find(".")] +os.sep))    

def prepare_workspace(identifier,out_path):
    arguments = {}
    output_path = observe_path_for_existence(out_path + identifier + os.sep)        
    arguments["output_path"]   = output_path
    arguments["tmp"]           = observe_path_for_existence(output_path + "tmp"+os.sep)
    arguments["cellobjects"]   = observe_path_for_existence(output_path + "tmp/cellobjects_dump"+os.sep)
    arguments["results"]       = observe_path_for_existence(output_path + "results"+os.sep)
    arguments["csv_dump"]      = observe_path_for_existence(arguments["tmp"] + "csv_dump"+os.sep)
    return arguments  