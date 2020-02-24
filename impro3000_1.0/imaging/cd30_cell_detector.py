# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 14:15:26 2019

@author: patri
"""
import sys
sys.path.append("..")
from imaging import color_deconvolution
from imaging.cd30_cell_detector_lib import membrane_segmenter
from imaging.cd30_cell_detector_lib import measure

__SCRIPT_NAME = "[Cell detector]"

def detect(image,config,arguments,return_segmented=False,save_measurements=True):
    cd30,hem = color_deconvolution.colour_deconvolution(image)
    segmented = membrane_segmenter.segment(cd30, hem,config)
    if cd30.get_global_x() is None or cd30.get_global_y() is None:
        objects = measure.measure_objects(segmented, im_coords=[0,0])
        if len(objects)>0 and save_measurements:
            measure.write_measurements(objects,arguments["cellobjects"]+cd30.get_id()+".csv")
    else:
        objects = measure.measure_objects(segmented, im_coords=[cd30.get_global_x(), cd30.get_global_y()])
        if len(objects)>0 and save_measurements:
            measure.write_measurements(objects,arguments["cellobjects"]+cd30.get_id()+".csv")
    print(__SCRIPT_NAME+": Found " + str(len(objects))+ " cells inside " + image.get_name()+"_"+image.get_id())
    
    cd30 = None
    hem = None
    
    if return_segmented:
        
        return objects,segmented
    
    else:
        
        segmented = None
        
        return objects