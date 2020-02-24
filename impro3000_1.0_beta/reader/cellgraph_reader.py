# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 14:34:36 2018

@author: patri
"""
import sys
sys.path.append("..")
import argparse as ap
import graph_lib.CellGraph as Cellgraph_lib
import os
import inspect
import importlib.util
import multiprocessing as mp
from functools import partial
import time
from pathlib import Path
import timeit

iprop = True

__ScriptName = "[Cellgraph_reader]"

def __parse_arguments():
    parser = ap.ArgumentParser()
    # path to image file, that will be read:
    parser.add_argument("-i", "--import_path", help="enter path to the graphfolder", type=str, default= "C:/Users/patri/OneDrive/Dokumente/Promotion/Graphen/cells_csv/")
    parser.add_argument("-iprop", "--improproperties", help="improproperty files or impro graph file?", type=str, default= True)
    # path to a directory to save image tiles to. this is required for one of the Imaging Library modules, not the SVS-Reader istself. 
    parser.add_argument("-o", "--output_path", help="enter the desired output path, not including the image name", type=str, default="../workspace3000/gcb_joerg/")    
    # path to a directory to save image tiles to. this is required for one of the Imaging Library modules, not the SVS-Reader istself. 
    parser.add_argument("-graphpipe", "--graph_processing_pipeline_path", help="enter the path to your postprocessing pipeline script, including the pipeline name", type=str, default="../pipelines/pipeline_mosbach.py")
    parser.add_argument("-impro_path", "--impro_path", help="impro_path", type=str, default="../")
    parser.add_argument("-mp", "--multiprocessed", help="Multiprocessed?", type=str, default=True)
    parser.add_argument("-eval", "--evaluation", help="Property evaluation", type=str, default=True)
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
    arguments["nuclei"] = __observe_path_for_existence(path + "nuclei"+os.sep)
    arguments["cellobjects"] = __observe_path_for_existence(path + "cellobjects"+os.sep)
    arguments["tmp"] = __observe_path_for_existence(path + "tmp"+os.sep)
    arguments["results"] = __observe_path_for_existence(path + "results"+os.sep)
    return arguments

def __create_cellgraph(identifier,path,iprop):
    cellgraph = Cellgraph_lib.CellGraph(identifier,"cellobject")
    if ".gml" in path:
        cellgraph.load_graph_from_gml(path)
    if ".csv" in path:
        if iprop:
            cellgraph.load_vertices_from_improfile_with_properties(path)
        else:
            cellgraph.load_vertices_from_improfile(path)
    return cellgraph
    

def __identifyMain(pipePath):
    spec = importlib.util.spec_from_file_location("pipeline", pipePath)
    pipeline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pipeline)
    functionList = inspect.getmembers(pipeline,inspect.isfunction)
    for function in functionList:
        if function[0] == "main":
            return function[1]

def __startPipeline(file,graphpipe,library_path,out_path,iprop):
    identifier = os.path.basename(file).split(".")[0].split("_")[0]
    output_folder = __observe_path_for_existence(out_path + identifier + os.sep)
    print(__ScriptName+": analysing " + identifier)
    arguments = __prepare_workspace(output_folder)
    cellgraph = __create_cellgraph(identifier,file,iprop)
    main = __identifyMain(graphpipe)
    if cellgraph != None:
        main(None,cellgraph,arguments,library_path)
    else:
        print(__ScriptName + ": " + cellgraph.get_identifier()+"-cellgraph not found")

def __process_graphs(importPath,graphpipe,out_path,impro_path,multiprocessed,evaluation,iprop):
    folder = Path(importPath)
    if multiprocessed:
        pooledFunction = partial(__startPipeline,graphpipe=graphpipe,library_path=impro_path,out_path=out_path,iprop=iprop)
        fileNames = os.listdir(folder)
        fileNames = [importPath + file for file in fileNames]
        print(__ScriptName + ": using " + str(min(12,mp.cpu_count()-1)) + " cores!")
        pool = mp.Pool(processes=max(12,mp.cpu_count()-1))
        pool.map(pooledFunction,fileNames)
        pool.close()
    else: 
        for file in os.listdir(folder):
            __startPipeline(file,graphpipe,impro_path,out_path)
    if evaluation:
        os.system("python evaluator.py -i "+out_path+" -o " + out_path + "evaluation/")
    

if __name__ == '__main__':
    print(__ScriptName + ": Initiated! Lets go!")
    print(time.ctime())
    start_time = timeit.default_timer()
    args = __parse_arguments()
    importPath = os.path.abspath(args.import_path)+os.sep
    graphpipe = os.path.abspath(args.graph_processing_pipeline_path)
    impro_path = args.impro_path
    out_path = os.path.abspath(args.output_path)+os.sep
    multiprocessed= args.multiprocessed
    evaluation = args.evaluation
    iprop = args.improproperties
    __process_graphs(importPath,graphpipe,out_path,impro_path,multiprocessed,evaluation,iprop)
    stop_time = timeit.default_timer()
    print(__ScriptName + ": " + "-- it took forever: ", stop_time - start_time, " seconds --")