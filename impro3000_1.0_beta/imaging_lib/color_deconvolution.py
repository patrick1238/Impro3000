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
import basicfunctions

__SCRIPT_NAME="[COLOR_DECONVOLUTION]"

def load_color_matrix( stain,path=''):
    fileDir = os.path.dirname(os.path.realpath('__file__'))    
    color_matrix_file_relative = "".join(["../imaging_lib/color_deconvolution_lib/",str(stain).lower(), ".csv"])    
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
    print(__SCRIPT_NAME+" Color deconvolution started for: " + image.get_name())
    stain = ""
    if stain2 == "":
        stain = stain1
    else:
        stain = stain1 + "_" + stain2
    color_matrix = np.linalg.inv(load_color_matrix(stain, path=path))
    image_hematox_CD30_rest = separate_stains(image_numpy,color_matrix)
    image_hematox_CD30_rest = rescale_intensity(image_hematox_CD30_rest,out_range=(0,255))
    image_hematox_CD30_rest = image_hematox_CD30_rest.astype(np.uint8)

    hematox = image.get_new_instance()
    hematox.set_staining(stain1)
    hematox_channel = basicfunctions.intensity_values_to_byte(image_hematox_CD30_rest[:, :, 1])
    hematox_channel[hematox_channel <= 100] = 0
    hematox.set_numpy_array(hematox_channel)
    
    cd30 = image.get_new_instance()
    cd30.set_staining(stain2)
    print(np.nonzero(image_hematox_CD30_rest[:, :, 0]))
    cd30_channel = basicfunctions.intensity_values_to_byte(image_hematox_CD30_rest[:, :, 0])
    print(np.nonzero(cd30_channel))
    cd30_channel[cd30_channel <= 100] = 0
    print(np.nonzero(cd30_channel))
    cd30.set_numpy_array(cd30_channel)
    return cd30,hematox