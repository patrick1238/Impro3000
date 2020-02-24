# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 16:56:14 2018

@author: patri
"""
import sys
sys.path.append("..")
import networkx as nx
import graph.Cellgraph_lib.parser_lib as parser
import graph.Cellgraph_lib.initiate_edge_lib as edge_lib
import graph.Cellgraph_lib.binning_lib as binning_lib
import graph.Analysing_lib.analyse as analyser
import matplotlib.pyplot as plt
import graph.Cellgraph_lib.graph_visualization_lib as gvl
import graph.Cellgraph_lib.colocalizer_lib as coloc_lib

class CellGraph:
    
    __nxGraph = None
    __celldiameter = 70
    __nucleidiameter = 10
    __id = 0
    __featureset = None
    
    __SCRIPT_NAME = "[Cell graph]"

    def __init__(self,identifier="default", diagnose = "unknown", stain = "CD30"):
        self.__nxGraph = nx.Graph()
        self.__nxGraph.graph["name"] = identifier
        self.__nxGraph.graph["diagnose"] = diagnose
        self.__nxGraph.graph["stain"] = stain
        self.__nxGraph.graph["mode"] = "not initiated"
        
    def add_node(self,position,attributes=None):
        if attributes != None:
            self.__nxGraph.add_node(self.__id)
            attributes["position"]=position
            attributes["label"]=self.__id
            for feature in attributes:
                self.__nxGraph.node[self.__id][feature]=attributes[feature]
        else:
            self.__nxGraph.add_node(self.__id,position=position,label=self.__id)
        self.__id = self.__id + 1
        
    def add_edge(self,node1,node2,distance=None):
        if distance != None:
            self.__nxGraph.add_edge(node1,node2,distance=distance)
        else:
            self.__nxGraph.add_edge(node1,node2)
        
    def get_identifier(self):
        return self.__nxGraph.graph["name"]
    
    def set_identifier(self,identifier):
        self.__nxGraph.graph["name"] = identifier
    
    def get_nodes(self,attribute=None):
        if attribute == None:
            return dict(self.__nxGraph.nodes(data=True))
        else:
            return dict(self.__nxGraph.nodes(data=attribute))#nx.get_node_attributes(self.__nxGraph,attribute)
    
    def get_edges(self):
        return self.__nxGraph.edges(data=True)
    
    def set_graph_mode(self,mode):
        self.__nxGraph.graph["mode"] = mode
        
    def get_graph_mode(self):
        return self.__nxGraph.graph["mode"]
    
    def get_diagnose(self):
        return self.__nxGraph.graph["diagnose"]
    
    def set_diagnose(self,diagnose):
        self.__nxGraph.graph["diagnose"] = diagnose

    def get_nxgraph(self):
        return self.__nxGraph
    
    def set_nxgraph(self,nxgraph):
        self.__nxGraph = nxgraph

    def get_stain(self):
        return self.__nxGraph.graph["stain"]
    
    def set_stain(self,stain):
        self.__nxGraph.graph["stain"] = stain
        
    def analyse(self,two_color=False,attribute="stain"):
        self.__featureset = analyser.analyse(self,two_color,attribute)
        self.__featureset.print_features()           
        
    def save_analysis(self,folder):
        self.__featureset.save_as_impro_properties_file(folder)
        
    def display(self):
        print(nx.info(self.__nxGraph))
        print(str(self.__nxGraph.graph).strip("{").strip("}").strip("'"))
        nx.draw(self.__nxGraph,pos=nx.get_node_attributes(self.__nxGraph,'position'),label=nx.get_node_attributes(self.__nxGraph,'label'),font_size=16)
        nx.draw_networkx_labels(self.__nxGraph,pos=nx.get_node_attributes(self.__nxGraph,'position'),label=nx.get_node_attributes(self.__nxGraph,'label'),font_size=16)
        
    def info(self):
        print(nx.info(self.__nxGraph))
        print("Diagnose: " + self.__nxGraph.graph["diagnose"])
        print("Objects: " + self.__nxGraph.graph["object"])
        print("Mode: " + self.__nxGraph.graph["mode"])
            
    def load_graph_from_gml(self,path):
        self.__nxGraph = nx.read_gml(path)

    def load_vertices_from_improfile(self,path):
        parser.parse_vertices_impro(self,path)
        
    def load_vertices_from_imaris(self,path):
        parser.parse_vertices_imaris(self, path)
    
    def colocalize_nodes(self,dimension=3):
        coloc_lib.colocalize_cells(self,dimension)
        
    def initiate_edges(self,mode=None,communication_treshold=700,dimension=2):
        if mode == "Deterministic" or mode == None:
            edge_lib.initialize_deterministic_graph(self,communication_treshold,dimension)
        elif mode == "Waxmann":
            edge_lib.initialize_waxmann_graph(self,communication_treshold,dimension)
        elif mode == "Waxmann_extended":
            edge_lib.initialize_extended_waxmann_graph(self,communication_treshold,dimension)
            
    def clear_edges(self):
        self.__mode = "Not_initiated"
        edges = list(self.__nxGraph.edges().keys())
        self.__nxGraph.remove_edges_from(edges)
            
    def save_as_gml(self,path):
        new_path = path+self.__nxGraph.graph["name"]+"_"+self.__nxGraph.graph["mode"]+".gml"
        nx.write_gml(self.__nxGraph, new_path)
        
    def save_as_impro_coloc_file(self,path):
        output = parser.convert_graph_to_csv(self)
        outpath = path + self.__nxGraph.graph["name"] + ".icf"
        file = open(outpath,"w")
        file.write(output)
        file.close()
        return outpath
        
    def save_as_png(self,path,background_image=None,highlight_nodes=[],highlight_edges=[],upperleft=(0,0),layer=0,descriptor="printed"):         
        size = (1000000,1000000)
        if background_image is not None:
            plt.imshow(background_image)
            size = background_image.shape
        ids,positions = gvl.get_nodes(self.__nxGraph,upperleft,size,layer,highlight_nodes)
        if len(highlight_nodes)>0:
            nx.draw_networkx_nodes(self.__nxGraph,positions,highlight_nodes, zorder=0, node_size=0.05, node_color="green", alpha=0.7, width=0.05,  with_labels=False)
        nx.draw_networkx_nodes(self.__nxGraph,positions,ids, zorder=0, node_size=0.05, node_color="black", alpha=0.7, width=0.05,  with_labels=False)
        edges = gvl.get_edges(self.__nxGraph,ids+highlight_nodes,highlight_edges)
        nx.draw_networkx_edges(self.__nxGraph,positions,edges,width=0.05)
        if background_image is None:
            plt.gca().invert_yaxis()
        plt.axis('off')
        output_path = path+self.__nxGraph.graph["name"]+"_"+self.__nxGraph.graph["mode"] + "_" + descriptor +".tiff"
        plt.savefig(output_path, dpi=1000, bbox_inches='tight')
        plt.clf()
        return output_path
        
    def get_new_instance(self):
        return CellGraph(self.__nxGraph.graph["name"], self.__nxGraph.graph["diagnose"], self.__nxGraph.graph["stain"])