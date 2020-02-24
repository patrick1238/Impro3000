# -*- coding: utf-8 -*-
"""
Created on Fri May  3 10:03:06 2019

@author: patri
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append("..")

from skimage.morphology import watershed

from skimage.feature import peak_local_max
from scipy import ndimage
import imaging_lib.CellDetector_lib.measure as ms

def detect(image,arguments):
    image_numpy = image.get_numpy_array()    
    plt.axis('off')  
    threshold = 220#np.percentile(np.array(image_numpy),95)
    mask = image_numpy > threshold
    mask = ndimage.filters.median_filter(mask,size=20)
    mask = ndimage.binary_closing(mask,iterations=20)
    mask = ndimage.binary_fill_holes(mask)
    label_im, nb_labels = ndimage.label(mask)
    sizes = ndimage.sum(mask, label_im, range(nb_labels + 1))
    mask_size = sizes < 180000000   
    remove_pixel = mask_size[label_im]    
    remove_pixel.shape
    label_im[remove_pixel] = 0
    labels = np.unique(label_im)
    label_im = np.searchsorted(labels, label_im)
    distance = ndimage.distance_transform_edt(label_im)
    local_maxi = peak_local_max(distance, indices=False, footprint=np.ones((80, 80)),labels=label_im)
    markers,cells = ndimage.label(local_maxi)
    labels_watershed = watershed(-distance, markers, mask=label_im)
    print(image.get_id() + ": " + str(cells))
    measurer = ms.Measurer()
    measurer.measure_objects(labels_watershed,cells)
    measurer.write_measurements(arguments["tmp"]+image.get_id()+"_cells.csv")