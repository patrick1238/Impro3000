# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 17:19:04 2019

@author: Hodgkin
"""

import sys
sys.path.append("..")
from imaging import color_deconvolution
from imaging import follicle_detector
from imaging import validator
from reader.WSI_reader_lib import Config
from scipy import misc
from imaging import roi_detector
import numpy as np

def main(image,arguments):
    config = Config.Config(parse_cmd=False)
    roi = roi_detector.detect_roi(image.get_numpy_array())
    misc.imsave(arguments["tmp"]+image.get_name()+"_roi.tif",roi)
    actin,other = color_deconvolution.colour_deconvolution(image,image.get_staining()[0])
    mask,objects = follicle_detector.detect(actin,roi,arguments)
    results = validator.validate_results(mask,image.get_name(),config.get("validation_folder"),arguments,objects,True) 
    print(results)
    misc.imsave(arguments["results"]+image.get_name()+"_follicle_mask.tif",mask)