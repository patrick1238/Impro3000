# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 11:55:00 2019

@author: patri
"""
import region_of_interest as roi
import numpy as np
from scipy import misc, ndimage

__SCRIPT_NAME="[General Properties]"

def measure_general_properties(image,arguments):
    print(__SCRIPT_NAME+": Measuring general properties of " + image.get_id())
    output = {}
    a = image.get_numpy_array()
    roi_array = roi.calculateROI(a,1300,"",220,"ROI")
    misc.imsave(arguments["tmp"]+image.get_id()+"_roi.tif",roi_array)
    tissue_size = measure_size(roi_array)
    output["tissue_size"] = tissue_size
    import color_deconvolution
    cd30_image_object, hematoxilin_image_object = color_deconvolution.colour_deconvolution(image)
    cd30_positive_pixel = np.multiply(cd30_image_object.get_numpy_array(),roi_array)
    cd30_positive_pixel[cd30_positive_pixel <= 80] = 0
    label_im, nb_labels = ndimage.label(cd30_positive_pixel)
    sizes = ndimage.sum(cd30_positive_pixel, label_im, range(nb_labels + 1))
    mask_size = sizes > 1000
    remove_pixel = mask_size[label_im]
    label_im[remove_pixel] = 0
    stained_pixels = measure_size(label_im)
    output["primarystained_tissue"] = stained_pixels
    output["proportion"] = stained_pixels/(tissue_size/100)
    return output

    

def measure_size(array):
    tissue_pixel=np.count_nonzero(array)
    return (tissue_pixel*(0.2467*32))/1000000