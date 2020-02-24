# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 16:56:14 2018

@author: patri
"""
import sys
sys.path.append("..")
import networkx as nx
import numpy as np
import os
import graph_lib.CellGraph_lib.parser_lib as parser
import graph_lib.CellGraph_lib.initiate_edge_lib as edgeLib
import graph_lib.CellGraph_lib.observer_lib as observer
import graph_lib.Analysing_lib.analyse as analyser

class CellGraph:
    
    __identifier = "default"
    __nxGraph = None
    __mode = "Not_initiated"
    __celldiameter = 50
    __nucleidiameter = 10
    __objectdescription = None
    
    def __init__(self,identifier=None, objectdescription = "nuclei"):
        self.__identifier = identifier
        self.__nxGraph = nx.Graph()
        self.__objectdescription = objectdescription
        
    def add_node(self,nodeID,position,attributes=None):
        self.__nxGraph.add_node(nodeID,position=position,label=nodeID)
        if attributes != None:
            nx.set_node_attributes(self.__nxGraph, attributes)
        
    def add_edge(self,node1,node2):
        self.__nxGraph.add_edge(node1,node2)
        
    def addSubgraphViaCSV(self,csvPath):
        with open(csvPath,"r") as file:
            header = file.readline()
            for line in file.readlines():
                nodeID,position,attributes = parser.parseCSVLine(line,header)
                if nodeID != "":
                    observe = True
                    if self.__objectdescription == "nuclei":
                        observe = observer.observe_for_doubled_entry(self.get_attributes_as_array("position","float"),position,self.__nucleidiameter)
                    else:
                        pass
                        #observe = observer.observe_for_doubled_entry(self.get_nodes(),position,self.__celldiameter)
                    if observe:
                        self.add_node(nodeID,position,attributes)
            file.close()
        
    def addSubgraphViaGML(self,gmlPath):
        print("Not yet implemented copyright Hendrik Schaefer")
        
    def get_identifier(self):
        return self.__identifier
    
    def get_nodes(self):
        return nx.get_node_attributes(self.__nxGraph,'position')
    
    def get_edges(self):
        return self.__nxGraph.edges
    
    def set_graph_mode(self,mode):
        self.__mode = mode
        
    def get_graph_mode(self):
        return self.__mode

    def get_nxgraph(self):
        return self.__nxGraph

    def get_attributes_as_array(self,attribute,attribute_type=None):
        attribute_array = []
        for value in nx.get_node_attributes(self.__nxGraph,attribute).values():
            attribute_array.append(value)
        if attribute_type == "float":
            return np.array(attribute_array).astype(float)
        elif attribute_type == "int":
            return np.array(attribute_array).astype(int)
        else:
            return np.array(attribute_array)
        
    def load_graph_from_gml(self,path):
        self.__nxGraph = nx.read_gml(path)

    def load_graph_from_improfile(self,path):
        basename = os.path.basename(path)
        self.__identifier = basename[basename.rfind('_')+1:basename.rfind('.')]
        parser.parseFullImproGraph(self,path)

    def load_vertices_from_improfile(self,path):
        basename = os.path.basename(path)
        self.__identifier = basename[basename.rfind('_')+1:basename.rfind('.')]
        parser.parseImproGraphVertices(self,path)
        
    def load_vertices_from_improfile_with_properties(self,csvPath):
        with open(csvPath,"r") as file:
            header = file.readline()
            x=1
            for line in file.readlines():
                nodeID,position,attributes = parser.parseCSVLine(line,header,x)
                if nodeID != "":
                    observe = True
                    if self.__objectdescription == "nuclei":
                        observe = observer.observe_for_doubled_entry(self.get_attributes_as_array("position","float"),position,self.__nucleidiameter)
                    else:
                        pass
                        #observe = observer.observe_for_doubled_entry(self.get_nodes(),position,self.__celldiameter)
                    if observe:
                        self.add_node(nodeID,position,attributes)
                x += 1
            file.close()
    
    def initiate_edges(self,mode=None,communication_treshold=700):
        if mode == "Deterministic" or mode == None:
            edgeLib.initialize_deterministic_graph(self,communication_treshold)
        elif mode == "Waxmann":
            edgeLib.initialize_waxmann_graph(self,communication_treshold)
        elif mode == "Waxmann_extended":
            edgeLib.initialize_extended_waxmann_graph(self,communication_treshold)
            
    def clear_edges(self):
        self.__mode = "Not_initiated"
        edges = list(self.__nxGraph.edges().keys())
        self.__nxGraph.remove_edges_from(edges)
    
    def get_description(self):
        return self.__objectdescription
    
    def analyse(self,arguments):
        return analyser.analyse(self,arguments)
    
    def save_as_gml(self,path):
        new_path = path+self.__identifier+"_"+self.__mode+".gml"
        nx.write_gml(self.__nxGraph, new_path)
        
    def display(self):
        print(nx.info(self.__nxGraph))
        print(str(self.__nxGraph.graph).strip("{").strip("}").strip("'"))
        nx.draw(self.__nxGraph,pos=nx.get_node_attributes(self.__nxGraph,'position'),label=nx.get_node_attributes(self.__nxGraph,'label'),font_size=16)
        nx.draw_networkx_labels(self.__nxGraph,pos=nx.get_node_attributes(self.__nxGraph,'position'),label=nx.get_node_attributes(self.__nxGraph,'label'),font_size=16)
        
    def info(self):
        print(nx.info(self.__nxGraph))
        print(str(self.__nxGraph.graph).strip("{").strip("}").strip("'"))
        
        
        