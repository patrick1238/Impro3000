# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 11:06:02 2019

@author: patri
"""
import sys
sys.path.append("..")
import WSI
from imaging import image, color_deconvolution
from scipy import misc
from imaging import roi_detector

def get_staining(imagepath):
    stain = imagepath.split("_")[1]
    if "." in stain:
        stain = stain[:stain.find(".")]
    return stain

def analyse(imagepath,config):
    wsi = WSI.WSI(imagepath)
    stain = get_staining(imagepath)
    layer = int(config.get("preanalysis_layer"))
    image_object = image.Image(str(layer),wsi.get_image_name(),wsi.get_RGB_numpy_array(layer=layer),0,0,wsi.get_width(layer),wsi.get_height(layer),layer,stain)
    np_array = image_object.get_numpy_array()
    roi = roi_detector.detect_roi(np_array)
    prim,sec = color_deconvolution.colour_deconvolution(image_object,stain)
    misc.imsave(config.get("output_path")+image_object.get_name()+"_"+str(image_object.get_staining())+"_"+image_object.get_id()+".png",prim.get_numpy_array())