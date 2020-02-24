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
from scipy import misc
import WSI

def main(graph,arguments):
    img = nd.imread("C:/Users/patri/OneDrive/Dokumente/develop/impro3000/branches/impro3000_1.0/workspace3000/K120-12/results/K120-12_2.0.0.png")
    #wsi_object = WSI.WSI("C:/Users/patri/OneDrive/Dokumente/Promotion/Images/CD30withCD20CD3/2012/CD30/K120-12_CD30.svs")
    #tmp_nparray = wsi_object.get_RGB_numpy_array(10000,10000,2000,2000, 0)
    graph.initiate_edges()
    graph.save_as_png(arguments["results"],img,layer=2)#,tmp_nparray)
    