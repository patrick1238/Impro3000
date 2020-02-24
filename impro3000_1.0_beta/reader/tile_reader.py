# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 13:40:41 2018

@author: patri
"""
import sys
sys.path.append("..")

import argparse as ap
import imaging_lib.ImageObject as imageObject
import os
from scipy import misc
import numpy as np
import inspect
import importlib.util
import multiprocessing as mp
from functools import partial
import PostprocessingThread
import time
from pathlib import Path
import timeit

__SCRIPT_NAME = "[Tile Reader]"

def __parse_arguments():
    parser = ap.ArgumentParser()
    
    # specify the layer to be read:
    parser.add_argument("-l", "--layer", help="enter number of desired layer here", type=int, default=0)

    # path to image file, that will be read:
    parser.add_argument("-i", "--import_path", help="enter path to the tiledimagefolder", type=str, default= "../test_files/image/tiled_layer0/")#"E:/Users/Hodgkin/Desktop/develop/branches/impro3000_1.0_beta/test_files/image/test")
    
    # path to the pipeline script:
    parser.add_argument("-pipe", "--pipeline_path", help="enter the path to your pipeline script, including the pipeline name", type=str, default="../pipelines/prepipe_test.py")

    # path to a directory to save image tiles to. this is required for one of the Imaging Library modules, not the SVS-Reader istself. 
    parser.add_argument("-o", "--output_path", help="enter the desired output path, not including the image name", type=str, default="../workspace3000/")
    
    # path to a directory to save image tiles to. this is required for one of the Imaging Library modules, not the SVS-Reader istself. 
    parser.add_argument("-postpipe", "--postprocessing_pipeline_path", help="enter the path to your postprocessing pipeline script, including the pipeline name", type=str, default="../pipelines/postprocessingTest.py")
    parser.add_argument("-impro_path", "--impro_path", help="impro_path", type=str, default="../imaging_lib/")
    # list with all parsed cammand line inputs:
    args = parser.parse_args()
    return args

def __parseImageTileSpecification(tilePath,tile):
    width = tile[0].shape[0]
    height = tile.shape[0]
    tilePathSplitted = tilePath.split("_")
    objectID = tilePathSplitted[2]+"."+tilePathSplitted[3]+"."+tilePathSplitted[4].split(".")[0]
    globalX = int(tilePathSplitted[4].replace(".tif","")) * width
    globalY = int(tilePathSplitted[3]) * height
    layer = int(tilePathSplitted[2])
    staining = tilePathSplitted[1]+",Hematoxilin"
    return objectID,tile,globalX,globalY,width,height,layer,staining

def __identifyMain(pipePath):
    spec = importlib.util.spec_from_file_location("pipeline", pipePath)
    pipeline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pipeline)
    functionList = inspect.getmembers(pipeline,inspect.isfunction)
    for function in functionList:
        if function[0] == "main":
            return function[1]
            
def __createImageObject(name,importPath,layer):
    currentTile = np.array(misc.imread(importPath+name))
    objectID,array,globalX,globalY,width,height,layerCur,staining=__parseImageTileSpecification(name,currentTile)
    if layerCur == layer:
        return imageObject.ImageObject(objectID,__get_identifier(importPath),array,globalX,globalY,width,height,layerCur,staining)
    else:
        print("did not create image object: current layer (", layerCur, ") != specified layer (", layer, ")")

def __startPipeline(name,importPath,preprocessing_pipe,layer,library_path,arguments):
    main = __identifyMain(preprocessing_pipe)
    tile = __createImageObject(name,importPath,layer)
    if tile != None:
        print(__SCRIPT_NAME + ": Imagingpipeline started")
        main(tile,arguments,library_path)
    else:
        print("no tile found in path ", importPath, " with name ", name)

def __get_identifier(importPath):
    return os.path.dirname(importPath).split(os.sep)[-1]

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
    
def __start_threads(arguments):
    threads = {}
    nuclei_thread = PostprocessingThread.PostprocessingThread(__get_identifier(importPath),arguments["nuclei"])
    nuclei_thread.start()
    threads["nuclei_thread"] = nuclei_thread
    cellobject_thread = PostprocessingThread.PostprocessingThread(__get_identifier(importPath),arguments["cellobjects"])
    cellobject_thread.start()
    threads["cellobject_thread"] = cellobject_thread
    return threads
    
def __close_threads(threads):
    cellgraphs = {}
    for key, thread in threads.items():
        cellgraphs[key] = thread.exit_and_get_cellgraph()
    return cellgraphs

def process_tiles(importPath,preprocessing_pipe,layer,out_path,impro_path,postprocessing_pipe):
    folder = Path(importPath)
    output_folder = __observe_path_for_existence(out_path + folder.stem + os.sep)
    arguments = __prepare_workspace(output_folder)
    threads = __start_threads(arguments)
    pooledFunction = partial(__startPipeline,importPath=importPath,preprocessing_pipe=preprocessing_pipe,layer=layer,library_path=impro_path,arguments=arguments)
    fileNames = os.listdir(importPath)
    pool = mp.Pool(processes=max(12,mp.cpu_count()-1))
    pool.map(pooledFunction,fileNames)
    pool.close()
    cellgraphs = __close_threads(threads)
    main = __identifyMain(postprocessing_pipe)
    print(__SCRIPT_NAME + ": Graphprocessing started")
    main(cellgraphs["nuclei_thread"],cellgraphs["cellobject_thread"],impro_path,arguments)
        
if __name__ == '__main__':
    print(__SCRIPT_NAME + ": Image analysis started on " + str(time.ctime()))
    start_time = timeit.default_timer()
    args = __parse_arguments()
    importPath = os.path.abspath(args.import_path)+os.sep
    preprocessing_pipe = os.path.abspath(args.pipeline_path)
    impro_path = args.impro_path
    layer = args.layer
    out_path = os.path.abspath(args.output_path)+os.sep
    postprocessing_pipe = os.path.abspath(args.postprocessing_pipeline_path)
    process_tiles(importPath,preprocessing_pipe,layer,out_path,impro_path,postprocessing_pipe)
    stop_time = timeit.default_timer()
    print(__SCRIPT_NAME + ": Image analysis finished, it took", stop_time - start_time, "seconds ")