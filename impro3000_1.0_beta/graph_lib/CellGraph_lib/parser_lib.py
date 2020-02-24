# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 10:08:06 2018

@author: patri
"""

import os

def parseCSVLine(line,header,cellid=None):
    headerSplitted = header.split(",")
    idPosition = -1
    xPosition = -1
    yPosition = -1
    index = 0
    attributes = {}
    values = line.split(",")
    for head in headerSplitted:
        head = head.strip("\n")
        if head == "":
            pass
        elif head == "ID":
            idPosition = index
        elif head == "X_Coordinate" or head == "coordX":
            xPosition = index
        elif head == "Y_Coordinate" or head == "coordY":
            yPosition = index
        else:
            attributes[head.replace(" ","")] = values[index].strip("\n")
        index += 1
    attributes["X"] = int(round(float(values[xPosition])))
    attributes["Y"] = int(round(float(values[yPosition])))
    if cellid == None:
        return values[idPosition],(int(round(float(values[xPosition]))),int(round(float(values[yPosition])))),{values[idPosition]:attributes}
    else:
        return cellid,(int(round(float(values[xPosition]))),int(round(float(values[yPosition])))),{cellid:attributes}
        
def __analyseCSVLine(cellgraph,line,initializeEdges):
    splitted = line.split(',')
    if splitted[0] != 'null':
        cellgraph.add_node(int(splitted[0]),(int(splitted[3]),
                                               int(splitted[4])))
    if splitted[1] != 'null':
        cellgraph.add_node(int(splitted[1]),(int(splitted[5]),
                                               int(splitted[6])))
    if splitted[2] != 'infinity' and initializeEdges:
        cellgraph.add_edge(int(splitted[0]),int(splitted[1]))
    return cellgraph
    
def parseFullImproGraph(cellgraph,path):
    metadata = {}
    metadata["Filename"] = os.path.split(path)[-1]
    graphFile = open(path,"r")
    line = graphFile.readline()
    while '#' in line:
        splitted = line.replace("#METADATA ","").split('=')
        metadata[splitted[0]] = splitted[1].strip('\n')
        line = graphFile.readline()
    for line in graphFile.readlines():
        cellgraph = __analyseCSVLine(cellgraph,line,True)
    #print("ImproGraph parsed")
    #cellgraph.setMetaData(metadata)
    cellgraph.set_graph_mode("Deterministic")
    
def parseImproGraphVertices(cellgraph, path):
    metadata = {}
    metadata["Filename"] = os.path.split(path)[-1]
    graphFile = open(path,"r")
    line = graphFile.readline()
    while '#' in line:
        splitted = line.replace("#METADATA ","").split('=')
        metadata[splitted[0]] = splitted[1].strip('\n')
        line = graphFile.readline()
    for line in graphFile.readlines():
        cellgraph = __analyseCSVLine(cellgraph,line,False)
    #print("Vertices parsed")
    #cellgraph.setMetaData(metadata)
    
    