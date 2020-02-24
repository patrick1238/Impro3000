# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 10:38:51 2020

@author: patri
"""
import sys
sys.path.append("..")
from std_pckgs import Config
from WSI_reader_lib import Tile_provider
from imaging import roi_detector
from functools import partial
import javabridge as jv
import bioformats as bf
import Postprocessing_thread as post_thread
import multiprocessing as mp
import os
import time
from reader.std_pckgs.basic_functions import identify_main
from reader.std_pckgs.basic_functions import prepare_workspace
import read_lif
import time
import numpy as np
from skimage.external import tifffile as tif
from scipy import ndimage as nd
from skimage import feature
import itk
import SimpleITK as sitk
import sknw
import networkx as nx


def analyse_image(in_path,config):
    reader = read_lif.Reader('C:/Users/patri/OneDrive/Dokumente/Promotion/Images/3D/K887-16_LA_Aktin_594_63x001.lif')
    series = reader.getSeries()
    print(series[0].getMetadata())
    print(series[1].getMetadata())
    
    chosen = series[0]  # choose first image in the lif file
    image = chosen.getFrame(T=0, channel=1)  # image is a numpy array, first time point & second channel
    #tif.imsave('3dtest_start.tif', image, bigtiff=True)
    image = np.where(image<10,0,image)
    prepipe = identify_main(config.get("pipeline"))
    prepipe(image,config)

if __name__ == '__main__':
    start = time.time()
    config = Config.Config()
    in_path = config.get("input_path")
    if os.path.isdir(in_path):
        for file in os.listdir(in_path):
            file = in_path+file
            if os.path.isfile(file):
                analyse_image(file,config)
    if os.path.isfile(in_path):
        analyse_image(in_path,config)
    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Image analysis took "+("{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)))
    jv.kill_vm()