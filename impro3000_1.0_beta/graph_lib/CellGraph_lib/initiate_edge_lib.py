# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 13:37:33 2018

@author: patri
"""
import math
import numpy as np
import graph_lib.CellGraph_lib.binning_lib as binning_lib
import graph_lib.CellGraph_lib.Rectangle as rect
import matplotlib.pyplot as plt

__alpha = 1
__beta = 1
    
__cellDiameter = 70


def __get_distance(point1,point2):
    return math.sqrt(((point1[0]-point2[0])**2+(point1[1]-point2[1])**2))

def __get_probability_array(communication_threshold):
    probabilityArray = []
    for i in range(0,communication_threshold):
        probabilityArray.append(__alpha*math.e**(-(float(i)/float(__beta*communication_threshold))))
    plt.plot(range(0,communication_threshold),probabilityArray)
    plt.xlabel("Distance in pixel")
    plt.ylabel("Probability")
    plt.title("Distance based interaction probability of the used Waxman model")
    plt.savefig("probability_array.png",dpi=1200)
    return probabilityArray

def __get_communication_probability(distance,cellNumber,probabilityArray,communication_threshold):
    return probabilityArray[int(distance)] * ((1.-(float(__cellDiameter)/float(communication_threshold/2)))**cellNumber)

def __get_communication_area(point1,point2):
    vector = np.array([(point2[0]-point1[0]),(point2[1]-point1[1])])
    clockwise = np.array([vector[1],-vector[0]])
    counterClockwise = np.array([-vector[1],vector[0]])
    return rect.Rectangle(point1+clockwise,point1+counterClockwise,
                          point2+clockwise,point2+counterClockwise)

def __get_cellnumber_inside_communicationarea(nodes,point1,point2,binned,communication_threshold):
    counter = 0
    area = __get_communication_area(point1,point2)
    nodesToBeAnalysed = binning_lib.getCommunicationAreaBins(point1,point2,area,binned,communication_threshold)
    for key in nodesToBeAnalysed:
        if nodes[key] != point1 and nodes[key] != point2:
            if __get_distance(nodes[key],point1) < communication_threshold and __get_distance(nodes[key],point2) < communication_threshold:
                if area.contains_Point(nodes[key]):
                    counter += 1
    return counter

def __analyse_bin(cellgraph,binned,y,perpendicular,extended,communication_threshold):
    probabilityArray = __get_probability_array(communication_threshold)
    x = 0
    nodes = cellgraph.get_nodes()
    for horitzontal in perpendicular:
        coordinates = binning_lib.get_corresponding_bins(x,y,binned)
        for key in horitzontal:
            for key2 in coordinates:
                if key != key2:
                    distance = __get_distance(nodes[key],nodes[key2])
                    if distance < communication_threshold:
                        cellNumber = 0
                        if extended:
                            cellNumber = __get_cellnumber_inside_communicationarea(nodes,nodes[key],nodes[key2],binned,communication_threshold)
                        commmunicationProbability = __get_communication_probability(distance,cellNumber,probabilityArray,communication_threshold)
                        if np.random.sample() <= commmunicationProbability:
                            cellgraph.add_edge(key,key2)
        x += 1

def initialize_deterministic_graph(cellgraph, communication_threshold):
    binned = binning_lib.bin_cellgraph(cellgraph)
    nodes = cellgraph.get_nodes()
    x = 0
    y = 0
    for perpendicular in binned:
        for horitzontal in perpendicular:
            coordinates = binning_lib.get_corresponding_bins(x,y,binned)
            for key in horitzontal:
                for key2 in coordinates:
                    if key != key2:
                        distance = __get_distance(nodes[key],nodes[key2])
                        if distance < communication_threshold:
                            cellgraph.add_edge(key,key2)
            x += 1
        y += 1
        x = 0
    cellgraph.set_graph_mode("Deterministic")
    
def initialize_waxmann_graph(cellgraph,communication_threshold):
    binned = binning_lib.bin_cellgraph(cellgraph)
    y = 0
    for perpendicular in binned:
        __analyse_bin(cellgraph,binned,y,perpendicular,False,communication_threshold)
        y += 1
    cellgraph.set_graph_mode("Waxmann")
    
def initialize_extended_waxmann_graph(cellgraph, communication_threshold):
    binned = binning_lib.bin_cellgraph(cellgraph)
    y = 0
    for perpendicular in binned:
        __analyse_bin(cellgraph,binned,y,perpendicular,True,communication_threshold)
        y += 1
    cellgraph.set_graph_mode("Waxmann_extended")