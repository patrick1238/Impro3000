# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 14:34:36 2018

@author: patri
"""
import sys
sys.path.append("..")
import graph.Cell_graph as Cellgraph_lib
import os
import multiprocessing as mp
from functools import partial
import timeit
from std_pckgs import Config
from reader.std_pckgs.basic_functions import identify_main
from reader.std_pckgs.basic_functions import prepare_workspace
import std_pckgs.Diagnose_handler as diagnose_handler

iprop = True

__ScriptName = "[Cellgraph_reader]"

def __create_cellgraph(identifier,path,config):
    cellgraph = Cellgraph_lib.CellGraph(identifier,"cellobject")
    if ".gml" in path:
        cellgraph.load_graph_from_gml(path)
    if ".csv" in path:
        if config.get("parser") == "impro":
            cellgraph.load_vertices_from_improfile(path)
            handler = diagnose_handler.Diagnose_handler("diagnose_cellgraph")
            cellgraph.set_diagnose(handler.get(cellgraph.get_identifier()))
        if config.get("parser") == "imaris":
            #for sonja
            pass
    return cellgraph

def __startPipeline(file,config):
    if os.path.isfile(file):
        identifier = os.path.basename(file).split(".")[0].split("_")[0]
        print(__ScriptName+": analysing " + identifier)
        arguments = prepare_workspace(identifier,config.get("output_path"))
        cellgraph = __create_cellgraph(identifier,file,config)
        main = identify_main(config.get("graph_pipeline"))
        if cellgraph != None:
            main(cellgraph,arguments)
        else:
            print(__ScriptName + ": " + cellgraph.get_identifier()+"-cellgraph not found")
    else:
        print(__ScriptName+": File not available")

def __process_graphs(config):
    in_path = config.get("input_path")
    if os.path.isdir(in_path):
        pooledFunction = partial(__startPipeline,config=config)
        fileNames = os.listdir(in_path)
        fileNames = [config.get("input_path") + file for file in fileNames]
        pool = mp.Pool(processes=max(12,mp.cpu_count()-1))
        pool.map(pooledFunction,fileNames)
        pool.close()
    else:
        __startPipeline(in_path,config)
    
def __evaluate_analysed_graphs(config):
    main = identify_main(config.get("evaluation_pipeline"))
    main(config)    

if __name__ == '__main__':
    start_time = timeit.default_timer()
    config = Config.Config("Cellgraph_Reader_Config",parse_cmd=False)
    if config.get("graphprocessing_active")=="active":
        __process_graphs(config)
    if config.get("evaluation_active")=="active":
        __evaluate_analysed_graphs(config)
    stop_time = timeit.default_timer()
    print(__ScriptName + ": took: ", stop_time - start_time, " seconds")