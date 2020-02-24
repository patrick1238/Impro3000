# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 15:30:04 2018

@author: patri
"""

import sys

sys.path.insert(0,"..")

import threading
import time
import os
import graph_lib.CellGraph as cellgraphObject # works only if the svs_reader is started from the ../reader/ directory. else syspath doesn't know graph_lib location 

class PostprocessingThread(threading.Thread):
    
    __tmpPath = None
    __mainMethPostProcessingScript = None
    __cellgraph = None
    __exit_requested = False
    __finished = False
    __sleepTime = 1
    __SCRIPT_NAME = "[PostprocessingThread]"
    
    def __init__(self,identifier,tmpPath):
        super().__init__()
        path = os.path.dirname(tmpPath)
        self.__tmpPath = tmpPath
        self.__cellgraph = cellgraphObject.CellGraph(identifier,os.path.basename(path))
        if os.listdir(self.__tmpPath) != 0:
            print(self.__SCRIPT_NAME + ": Warning! Cleaning folder!")
            for file in os.listdir(self.__tmpPath):
                os.remove(file)
        
    def run(self):
        print(self.__SCRIPT_NAME + ": "+self.__cellgraph.get_description()+" collection started!")
        while self.__exit_requested == False or len(os.listdir(self.__tmpPath)) != 0:
            time.sleep(self.__sleepTime)
            if len(os.listdir(self.__tmpPath)) != 0:
                for file in os.listdir(self.__tmpPath):
                    path = self.__tmpPath+file
                    if os.path.isfile(path):
                        filename, file_extension = os.path.splitext(path)
                        if file_extension == ".isg":
                            self.__cellgraph.addSubgraphViaCSV(self.__tmpPath+file)
                            os.remove(self.__tmpPath+file)
        self.__finished = True

            
    def exit_and_get_cellgraph(self):
        self.__exit_requested = True
        while self.__finished == False:
            time.sleep(self.__sleepTime)
        print(self.__SCRIPT_NAME + ": "+self.__cellgraph.get_description()+" Datacollection finished!")
        return self.__cellgraph
    
    
            