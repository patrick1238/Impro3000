# -*- coding: utf-8 -*-
"""
Created on Thu May 23 17:31:44 2019

@author: patri
"""
import networkx as nx
import matplotlib.pyplot as plt
plt.rcdefaults()
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as nd
from PIL import Image, ImageDraw

def draw(hln,graph,path):
    #im = Image.open(path)
    im = Image.new("RGB",(4000,4000))
    d = ImageDraw.Draw(im)
    node_dict_tmp = nx.get_node_attributes(graph, "position")
    line_color = (255, 0, 0)
    for node in hln:
        point = node_dict_tmp[node]
        point1 = (int(point[0]/16),int(point[1]/16))
        if len(graph[node]) > 1:
            x = []
            y = []
            for neighbour in graph[node]:
                cur = node_dict_tmp[neighbour]
                x.append(cur[0])
                y.append(cur[1])
            point2 = (int(((sum(x)/len(x))/16)),int(((sum(y)/len(y))/16)))    
            #print(point1,point2)
            d.line([point1, point2], fill=line_color, width=2)
        else:
            d.point(point1, fill=line_color)
    #d.line([(0,0), (4000,4000)], fill=line_color, width=2)
    im.save(path.replace(".tiff","_test.tiff"))
    
def save_values_as_csv(graph,attributes,arguments):
    output = {}
    for attribute in attributes:
        node_dict_tmp = nx.get_node_attributes(graph, attribute)
        for node in node_dict_tmp:
            if node in output:
                output[node].append(node_dict_tmp[node])
            else:
                output[node] = [node_dict_tmp[node]]
    output_str = "id"
    for attribute in attributes:
        output_str = output_str + "," + str(attribute)
    output_str = output_str + "\n"
    out = []
    for node in output:
        output_str = output_str + str(node)
        for attribute in output[node]:
            out.append(attribute)
            output_str = output_str + "," + str(attribute)
        output_str = output_str + "\n"
    #print(sorted(out))
    file = open(arguments["results"] + "values.csv","w")
    file.write(output_str)
    file.close()
    
def neighbourhoud_analysis(graph,node,clusterc):
    nxgraph = graph.get_nxgraph()
    clustercoef = clusterc[node]
    neighbours = nxgraph[node].keys()
    for i in range(5):
        curclustercoef = 0
        counter = 0
        for node in neighbours:
            curclustercoef = curclustercoef + clusterc[node]
            counter = counter + 1
        newclustercoef = curclustercoef/counter
        if round(newclustercoef,2) < round(clustercoef,2):
            #print(round(newclustercoef,2), round(clustercoef,2))
            return False
        clustercoef = newclustercoef
        neighbours2 = []
        for node in neighbours:
            curlist = list(nxgraph[node].keys())
            for node in curlist:
                if node not in neighbours2:
                    neighbours2.append(node)
        neighbours = neighbours2
    return True

def __bin_array(array,highest):
    print(highest)
    counter = {}
    for i in np.arange(0,1.05,0.05):
        counter[i] = 0
    for value in array:
        old = 0
        for key in counter.keys():
            if value <= key:
                counter[old] = counter[old] + 1
                break
            old = key
    del counter[1]
    for key in counter:
        counter[key] = counter[key]/highest
    return counter            

def main(graph,arguments):
    img = nd.imread("C:/Users/patri/OneDrive/Dokumente/develop/impro3000/branches/impro3000_1.0/workspace3000/layer2_images/K120-12_2.0.0.png")
    for i in range(700,800,100):
        graph.initiate_edges(communication_treshold=i)
        nxgraph = graph.get_nxgraph()
        clusterc = nx.clustering(nxgraph)
        nx.set_node_attributes(nxgraph, clusterc, 'cc')
        degree_dict = {}
        for t in clusterc:
            degree_dict[t] = len(nxgraph[t])
        nx.set_node_attributes(nxgraph, degree_dict, 'degree')
        hln = []
        binned = __bin_array(clusterc.values(),sorted(list(clusterc.keys()))[-1]+1)
        #print(binned)
        y_pos = np.arange(20)#binned.keys()))
        plt.bar(y_pos, binned.values())
        plt.xticks(y_pos,[i/2 for i in range(20)])#binned.keys())
        plt.savefig(arguments["results"]+graph.get_identifier()+'01_cc_distrib.png')
        for t in clusterc:
            if clusterc[t] > 0.56 and clusterc[t] < 0.6:
                hln.append(t)
                #if neighbourhoud_analysis(graph,t,clusterc):
                    #hln.append(t)
        #print(len(hln))
        graph.clear_edges()
        #save_values_as_csv(nxgraph,["cc"],arguments)
        file_path = graph.save_as_png(arguments["results"],img,layer=2,highlight_nodes=hln,descriptor=str(i)+"b05606")
        graph.initiate_edges(communication_treshold=i)
        #draw(clusterc.keys(),nxgraph,file_path)
    