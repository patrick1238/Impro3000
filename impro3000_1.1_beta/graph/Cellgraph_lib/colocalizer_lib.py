# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 16:11:40 2019

@author: patri
"""

def major_axis_length_of_two_nodes(node1,node2):
    mal1 = 0
    mal2 = 0
    for key in node1:
        if "EllipsoidAxisLength" in key:
            mal1 = mal1 + float(node1[key])
    mal1 = mal1/3
    for key in node2:
        if "EllipsoidAxisLength" in key:
            mal2 = mal2 + float(node2[key])
    mal2 = mal2/3
    return max(mal1,mal2)

def identify_coloc_threshold(nodes):
    thresh = 1
    for node in nodes:
        for key in nodes[node]:
            if "EllipsoidAxisLength" in key:
                thresh = max(float(nodes[node][key]),thresh)
    return thresh

def colocalize_cells(cellgraph,dimension):
    cellgraph.clear_edges()
    nodes = cellgraph.get_nodes()
    coloc_threshold = identify_coloc_threshold(nodes)
    cellgraph.initiate_edges(communication_treshold=coloc_threshold,dimension=dimension)
    nxgraph = cellgraph.get_nxgraph()
    edges = cellgraph.get_edges()
    observer = []
    counter = 0
    for (u,v,d) in edges:
        if nodes[u]["stain"] != nodes[v]["stain"]:
            mal = major_axis_length_of_two_nodes(nodes[u],nodes[v])
            distance = d["distance"]
            if mal>distance:
                nxgraph.node[u]["doublestained"] = "true"
                id1 = nxgraph.node[v]["OriginalID"]
                id2 = nxgraph.node[u]["OriginalID"]
                if "colocobjects" in nxgraph.node[u].keys():
                    nxgraph.node[u]["colocobjects"].append(id1)
                else:
                    nxgraph.node[u]["colocobjects"] = [id1]
                nxgraph.node[v]["doublestained"] = "true"
                if "colocobjects" in nxgraph.node[v].keys():
                    nxgraph.node[v]["colocobjects"].append(id2)
                else:
                    nxgraph.node[v]["colocobjects"] = [id2]
                observer.append(u)
                observer.append(v)
                counter = counter + 1
    for node in nodes:
        if node not in observer:
            nxgraph.node[node]["doublestained"] = "false"
            nxgraph.node[node]["colocobjects"] = []
    cellgraph.clear_edges()
    cellgraph.set_nxgraph(nxgraph)
    print(cellgraph.get_identifier(),counter)