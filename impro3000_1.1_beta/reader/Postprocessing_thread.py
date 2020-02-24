# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 15:30:04 2018

@author: patri
"""

import sys

sys.path.append("..")

import threading
import time
import os
from graph import Cell_graph as cellgraph 
import graph.Cellgraph_lib.parser_lib as parser

class Postprocessing_thread(threading.Thread):

    __tmpPath = None
    __cellgraph = None
    __exit_requested = False
    __finished = False
    __sleepTime = 1
    __SCRIPT_NAME = "[PostprocessingThread]"

    def __init__(self,identifier,diagnose,stain,tmpPath):  
        super().__init__()
        path = os.path.dirname(tmpPath)
        self.__tmpPath = tmpPath
        self.__cellgraph = cellgraph.CellGraph(identifier,os.path.basename(path),diagnose,stain)
        if os.listdir(self.__tmpPath) != 0:
            for file in os.listdir(self.__tmpPath):
                os.remove(file)
        
    def run(self):
        while self.__exit_requested == False or len(os.listdir(self.__tmpPath)) != 0:
            time.sleep(self.__sleepTime)
            if len(os.listdir(self.__tmpPath)) != 0:
                for file in os.listdir(self.__tmpPath):
                    path = self.__tmpPath+file
                    if os.path.isfile(path):
                        filename, file_extension = os.path.splitext(path)
                        if file_extension == ".isg":
                            parser.parse_vertices(self.__cellgraph,self.__tmpPath+file)
                            os.remove(self.__tmpPath+file)
        self.__finished = True

            
    def exit_and_get_cellgraph(self):
        self.__exit_requested = True
        while self.__finished == False:
            time.sleep(self.__sleepTime)
        #self.__cellgraph.filter_for_duplicates()
        return self.__cellgraph
