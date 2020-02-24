# -*- coding: utf-8 -*-
"""
Impro3000

part of the Impro3000 project to replace shitty Impro stuff. Use with care...
"""
import numpy as np
from skimage.color import rgba2rgb
from skimage.color import separate_stains
import os
from skimage.exposure import rescale_intensity
import sys
sys.path.append("..")
from imaging import basicfunctions

__SCRIPT_NAME="[Color deconvolution]"

def load_color_matrix(stain,path=''):
    fileDir = os.path.dirname(os.path.realpath('__file__'))    
    color_matrix_file_relative = "".join(["../imaging/color_deconvolution_lib/",str(stain).lower(), ".csv"])    
    color_matrix_file = os.path.join(fileDir, color_matrix_file_relative)
    if (len(path) >= 2):
        color_matrix_file = path
    if not os.path.exists(color_matrix_file):
        print( __SCRIPT_NAME+" File '"+color_matrix_file+"' does not exist...skipping." )
        return None
    csv = np.genfromtxt (color_matrix_file, delimiter=",")
    return csv

def colour_deconvolution(image, stain1="CD30", stain2="", path=''):
    image_numpy = image.get_numpy_array()
    if len(image_numpy[0][0])==4:
        image_numpy = rgba2rgb(image_numpy)
    print(__SCRIPT_NAME+": Deconvolution of " + image.get_name() + "_" + image.get_id())
    stain = ""
    if stain2 == "":
        stain = stain1
    else:
        stain = stain1 + "_" + stain2
    color_matrix = np.linalg.inv(load_color_matrix(stain, path=path))
    three_channel_image = separate_stains(image_numpy,color_matrix)
    three_channel_image = rescale_intensity(three_channel_image,out_range=(0,255))
    three_channel_image = three_channel_image.astype(np.uint8)

    sec = image.get_new_instance()
    sec.set_staining(stain1)
    sec_channel = basicfunctions.intensity_values_to_byte(three_channel_image[:, :, 1])
    sec_channel[sec_channel <= 100] = 0
    sec.set_numpy_array(sec_channel)
    
    prim = image.get_new_instance()
    prim.set_staining(stain2)
    prim_channel = basicfunctions.intensity_values_to_byte(three_channel_image[:, :, 0])
    prim_channel[prim_channel <= 100] = 0
    prim.set_numpy_array(prim_channel)
    
    three_channel_image = None
    image_numpy = None
    
    return prim,sec