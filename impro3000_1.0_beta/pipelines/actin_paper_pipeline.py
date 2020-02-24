# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 13:22:59 2019

@author: patri
"""

import sys
sys.path.append("../imaging_lib/")
import color_deconvolution
import save_as_tiff
#import Follicle_detector
from scipy import misc
import numpy as np

def main(image_object, arguments, library_path):
    misc.imsave("input.tif",image_object.get_numpy_array())
    actin,other = color_deconvolution.colour_deconvolution(image_object,image_object.get_staining()[0])
    misc.imsave("test.tif",actin.get_numpy_array())
    #save_as_tiff.save_as_tiff(actin,arguments["tmp"])
    #Follicle_detector.detect(actin,arguments)