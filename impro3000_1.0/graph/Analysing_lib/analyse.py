# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 15:26:52 2018

@author: patri
"""

import graph.Analysing_lib.feature_set as fs
import networkx as nx
import numpy as np

def analyse(cellgraph,arguments):
    nxgraph = cellgraph.get_nxgraph()
    featureset = fs.feature_set(cellgraph)
    featureset = connectedness_and_cliquishness(nxgraph,featureset)
    featureset = property_based(nxgraph,featureset,arguments)
    featureset = distance_based(nxgraph,featureset)
    return featureset

#Global Graph Features for Connectedness and Cliquishness Measures
def connectedness_and_cliquishness(nxgraph,featureset):
    featureset.add_feature("Average_degree",__average_degree(nxgraph))
    featureset.add_feature("Density",nx.density(nxgraph))
    featureset.add_feature("Number_connected_components",nx.number_connected_components(nxgraph))
    featureset.add_feature("Giant_connected_component_ratio",__giant_connected_component_ratio(nxgraph))
    featureset.add_feature("Percentage_of_isolated_points",__percentage_of_isolated_points(nxgraph))
    featureset.add_feature("Percentage_of_end_points",__percentage_of_end_points(nxgraph))
    featureset.add_feature("Average_clustering_coefficient",nx.average_clustering(nxgraph))
    featureset.add_feature("Transitivity",nx.transitivity(nxgraph))
    return featureset

#Global Graph Features for Distance Based (Shortest-path related) Measures
def distance_based(nxgraph,featureset):
    featureset.add_feature("Number_of_nodes",nxgraph.number_of_nodes())
    featureset.add_feature("Number_of_edges",nxgraph.number_of_edges())
    #giant_connected_component = __get_giant_connected_component_nxgraph(nxgraph)
    #featureset.add_feature("Average_shortest_path_length",nx.average_shortest_path_length(giant_connected_component))
    #featureset.add_feature("Radius",nx.radius(giant_connected_component))
    #featureset.add_feature("Diameter",nx.diameter(giant_connected_component))
    return featureset

def property_based(nxgraph,featureset,arguments):
    features = {}
    for node,data in nxgraph.nodes(data=True):
        for attribute in data:
            if attribute != "position" and attribute != "X" and attribute != "Y" and attribute != "label":
                if attribute not in features:
                    features[attribute] = [float(data[attribute])]
                else:
                    features[attribute].append(float(data[attribute]))
    for feature in features:
        featureset.add_feature("Average_"+feature,np.average(features[feature]))
    return featureset

#Spectral features
def spectral_features(nxgraph,featureset):
    featureset.add_feature("Number_of_nodes",nxgraph.number_of_nodes())
    
def __average_degree(nxgraph):
    s = sum(dict(nxgraph.degree()).values())
    return (float(s) / float(nxgraph.number_of_nodes()))

def __giant_connected_component_ratio(nxgraph):
    return float(len(max(nx.connected_components(nxgraph), key=len)))/float(nxgraph.number_of_nodes())

def __percentage_of_isolated_points(nxgraph):
    return float(len(list(nx.isolates(nxgraph))))/float(nxgraph.number_of_nodes())

def __percentage_of_end_points(nxgraph):
    return float(len([x for x in nxgraph.nodes() if nxgraph.degree(x)==1]))/float(nxgraph.number_of_nodes())

def __get_giant_connected_component_nxgraph(nxgraph):
    copy = nxgraph.copy()
    cc = max(nx.connected_components(nxgraph), key=len)
    nodes = nxgraph.nodes()
    for node in nodes:
        if node not in cc:
            copy.remove_node(node)
    return copy

def __get_area_class(cell_area):
    area_class = -1
    if cell_area > 5000:
        area_class = 2
    elif cell_area < 2800:
        area_class = 0
    else:
        area_class = 1
    return area_class

def __bin_array(array):
    counter = {}
    for i in range(0,21):
        counter[i] = 0
    for value in array:
        counter[min(20,int(value/1000))] = counter[min(20,int(value/1000))]+1
    return counter

