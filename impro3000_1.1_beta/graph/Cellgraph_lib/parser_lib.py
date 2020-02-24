# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 10:08:06 2018

@author: patri
"""

def __parseCSVLine_impro(line,header):
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

def __parseCSVLine_imaris(line,header):
    headerSplitted = header.split(",")
    xPosition = -1
    yPosition = -1
    zPosition = -1
    index = 0
    attributes = {}
    values = line.split(",")
    for head in headerSplitted:
        head = head.strip("\n")
        if head == "" or head == "ID":
            attributes["OriginalID"] = values[index].strip("\n")
        elif head == "Position X":
            xPosition = index
        elif head == "Position Y":
            yPosition = index
        elif head == "Position Z":
            zPosition = index
        else:
            attributes[head.replace(" ","").replace("(","").replace(")","")] = values[index].strip("\n")
        index += 1
    attributes["X"] = int(round(float(values[xPosition])))
    attributes["Y"] = int(round(float(values[yPosition])))
    attributes["Z"] = int(round(float(values[zPosition])))
    position_tuple = (int(round(float(values[xPosition]))),int(round(float(values[yPosition]))), int(round(float(values[zPosition]))))
    return position_tuple,attributes      
    
def parse_vertices_impro(cellgraph, path):
    with open(path,"r") as file:
        header = file.readline()
        for line in file.readlines():
            position,attributes = __parseCSVLine_impro(line,header)
            cellgraph.add_node(position,attributes)
        file.close()   
        
def parse_vertices_imaris(cellgraph, path):
    with open(path, "r") as file:
        header = file.readline()
        holder = {}
        ident = 0
        for line in file.readlines():
            position,attributes = __parseCSVLine_imaris(line,header)
            holder[ident] = [position,attributes]
            ident += 1
        file.close()    
    for key in holder:
        cellgraph.add_node(holder[key][0],holder[key][1])
        
def convert_graph_to_csv(cellgraph):
    output = "origin"
    nodes = cellgraph.get_nodes()
    if len(nodes) > 0:
        for key in nodes[0].keys():
            if key != "position" and key != "label":
                output = output + "," + key
        output = output + "\n"
        for node in nodes:
            output = output + cellgraph.get_identifier()
            for key in nodes[node].keys():
                if key != "position" and key != "label":
                    if isinstance(nodes[node][key],list):
                        cur = ""
                        for value in nodes[node][key]:
                            cur = cur + "+" + str(value)
                        output = output  + "," + cur[1:]
                    else:
                        output = output  + "," + str(nodes[node][key])
            output = output + "\n"
    return output
    
    


    