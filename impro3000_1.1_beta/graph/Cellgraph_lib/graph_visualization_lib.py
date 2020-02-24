# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 12:44:21 2019

@author: patri
"""

import networkx as nx
import collections
import numpy as np

downsample = {0:1,1:4,2:16,3:32}

def get_nodes(graph,upperleft,size,layer,highlight_nodes):
    node_dict_tmp = nx.get_node_attributes(graph, "position")
    vertex_dictionary = collections.OrderedDict(sorted(node_dict_tmp.items()))
    pos = {}
    node_ids = []
    for vertex in vertex_dictionary:
        tmp_positions = vertex_dictionary.get(vertex)
        pos[vertex] = (int(np.round(tmp_positions[0]/downsample[layer])),int(np.round(tmp_positions[1]/downsample[layer])))
        if pos[vertex][0] >= upperleft[0] and pos[vertex][1] >= upperleft[1]:
            if pos[vertex][0] <= upperleft[0]+size[0] and pos[vertex][1] <= upperleft[1]+size[1]:
                if vertex not in highlight_nodes:
                    node_ids.append(vertex)
    return node_ids,pos

def get_edges(graph,nodes,highlight_edges):
    edgelist = []
    for edge in graph.edges():
        if edge[0] in nodes and edge[1] in nodes:
            if edge not in highlight_edges:
                edgelist.append(edge)
    return edgelist

