# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 14:42:29 2020

@author: patri
"""

import sys
sys.path.append("..")
import read_lif
import numpy as np


class Image3D():
    
    series = None
    
    def __init__(self,path):
        reader = read_lif.Reader('C:/Users/patri/OneDrive/Dokumente/Promotion/Images/3D/K887-16_LA_Aktin_594_63x001.lif')
        series = reader.getSeries()        
        chosen = series[0]  # choose first image in the lif file
        image = chosen.getFrame(T=0, channel=1)  # image is a numpy array, first time point & second channel
        #tif.imsave('3dtest_start.tif', image, bigtiff=True)
        image = np.where(image<10,0,image)
        
    def get_image():
        pass