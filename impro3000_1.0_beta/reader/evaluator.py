# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 11:30:10 2019

@author: patri
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 14:34:36 2018

@author: patri
"""
import sys
sys.path.append("..")
import argparse as ap
import os
import inspect
import importlib.util
import time
from pathlib import Path
import timeit
import evaluator_lib.result_collector as collector

iprop = True

__ScriptName = "[Evaluator]"

def __parse_arguments():
    parser = ap.ArgumentParser()
    # path to image file, that will be read:
    parser.add_argument("-i", "--import_path", help="enter path to the importfolder", type=str, default= "../workspace3000/gcb/")
    parser.add_argument("-o", "--output_path", help="enter the desired output path, not including the image name", type=str, default="../workspace3000/evaluation_mosbach/")
    parser.add_argument("-impro_path", "--impro_path", help="impro_path", type=str, default="../")
    parser.add_argument("-df", "--diagnosis_file", help="Diagnosis file for given ids?", type=str, default="../reader/evaluator_lib/diagnose.csv")
    parser.add_argument("-tr", "--train", help="Do you want to train the classifier?", type=str, default=True)
    parser.add_argument("-vl", "--visualize", help="Do you want to visualize your data?", type=str, default=False)
    parser.add_argument("-vl_pipe", "--visualization_pipeline", help="enter the path to your visualization pipeline, including the pipeline name", type=str, default="../pipelines/visualization_pipeline.py")
    parser.add_argument("-tr_pipe", "--training_pipeline", help="enter the path to your training pipeline, including the pipeline name", type=str, default="../pipelines/training_pipeline.py")

    # list with all parsed cammand line inputs:
    args = parser.parse_args()
    return args

def __observe_path_for_existence(path):
    file = Path(path)
    if not file.is_dir():
        os.makedirs(path)
    return path
    
def __prepare_workspace(path):
    arguments = {}    
    arguments["results"] = __observe_path_for_existence(path + "results"+os.sep)
    return arguments
    

def __identifyMain(pipePath):
    spec = importlib.util.spec_from_file_location("pipeline", pipePath)
    pipeline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pipeline)
    functionList = inspect.getmembers(pipeline,inspect.isfunction)
    for function in functionList:
        if function[0] == "main":
            return function[1]

def __startPipeline(feature_set,pipe,library_path,out_path):
    main = __identifyMain(pipe)
    main(feature_set,out_path)

def __visualize_results(importPath,vlpipe,out_path,impro_path,diagnosis_file):
    out_path = __observe_path_for_existence(out_path)
    result_files = collector.collect_result_files_for_visualization(importPath,diagnosis_file)
    reordered = collector.reorder_by_feature(result_files)
    __startPipeline(reordered,vlpipe,impro_path,out_path)
            
def __train_decision_tree(importPath,trpipe,out_path,impro_path,diagnosis_file):
    out_path = __observe_path_for_existence(out_path)
    result_files = collector.collect_result_files_for_training(importPath,diagnosis_file)
    #reordered = collector.reorder_by_feature(result_files)
    __startPipeline(result_files,trpipe,impro_path,out_path)

if __name__ == '__main__':
    print(__ScriptName + ": Initiated! Lets go!")
    print(time.ctime())
    start_time = timeit.default_timer()
    args = __parse_arguments()
    importPath = os.path.abspath(args.import_path)+os.sep
    vl = args.visualize
    tr = args.train
    impro_path = args.impro_path
    out_path = os.path.abspath(args.output_path)+os.sep
    diagnosis_file = args.diagnosis_file
    if vl:
        vlpipe = os.path.abspath(args.visualization_pipeline)
        __visualize_results(importPath,vlpipe,out_path,impro_path,diagnosis_file)
    if tr:
        trpipe = os.path.abspath(args.training_pipeline)
        __train_decision_tree(importPath,trpipe,out_path,impro_path,diagnosis_file)
    stop_time = timeit.default_timer()
    print(__ScriptName + ": " + "-- it took forever: ", stop_time - start_time, " seconds --")