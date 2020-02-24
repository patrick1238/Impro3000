# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 16:06:21 2019

@author: patri
"""

import time
import networkx as nx

def main(nuclei_graph,cellobject_graph,arguments,librarypath):
    print(time.ctime())
    #if len(cellobject_graph.get_edges()) == 0:
        #cellobject_graph.initiate_edges("Waxmann")
    #featureset = cellobject_graph.analyse()
    #featureset.print_features()
    cellobject_graph.initiate_edges("Waxmann")
    cellobject_graph.save_as_gml(arguments["results"])
    #cellobject_graph.info()
    features = cellobject_graph.analyse(arguments)
    features.save(arguments["results"])
    #output_string = "node_id,degree,cluster_coefficient\n"
    #graph = cellobject_graph.get_nxgraph()
    #for key in cellobject_graph.get_nodes().keys():
    #    output_string = output_string + str(key) + "," + str(graph.degree(key)) + "," + str(nx.clustering(graph,key)) + "\n"
    #file = open(arguments["results"] + cellobject_graph.get_identifier() + "_clustering_degree.csv","w")
    #file.write(output_string)
    #file.close()