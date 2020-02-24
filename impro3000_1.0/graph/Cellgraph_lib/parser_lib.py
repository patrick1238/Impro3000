# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 10:08:06 2018

@author: patri
"""

def __parseCSVLine(line,header):
    headerSplitted = header.split(",")
    xPosition = -1
    yPosition = -1
    index = 0
    attributes = {}
    values = line.split(",")
    for head in headerSplitted:
        head = head.strip("\n")
        if head == "" or head == "ID":
            pass
        elif head == "x" or head == "coordX":
            xPosition = index
        elif head == "y" or head == "coordY":
            yPosition = index
        else:
            attributes[head.replace(" ","")] = values[index].strip("\n")
        index += 1
    attributes["X"] = int(round(float(values[xPosition])))
    attributes["Y"] = int(round(float(values[yPosition])))
    position_tuple = (int(round(float(values[xPosition]))),int(round(float(values[yPosition]))))
    return position_tuple,attributes
    
def parse_vertices_from_improfile(cellgraph, path):
    with open(path,"r") as file:
        header = file.readline()
        for line in file.readlines():
            position,attributes = __parseCSVLine(line,header)
            cellgraph.add_node(position,attributes)
        file.close()
        
def parse_vertices_from_imarisfile(cellgraph, path):
    #for sonja
    pass
    
    