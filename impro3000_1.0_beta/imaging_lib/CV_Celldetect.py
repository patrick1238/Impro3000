# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 17:29:49 2019

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

def Detect_cells(cd30_image_object,arguments):
    cd30_image = cd30_image_object.get_numpy_array()    
    plt.figure(figsize=(9, 4))
    plt.subplot(131)
    plt.imshow(cd30_image, cmap='gray', interpolation='nearest')
    plt.axis('off')  
    threshold = np.percentile(np.array(cd30_image),95)
    print(threshold)
    mask = cd30_image > threshold
    mask = ndimage.filters.median_filter(mask,size=20)
    mask = ndimage.binary_closing(mask,iterations=20)
    plt.subplot(132)  
    plt.imshow(mask, interpolation='nearest')
    mask = ndimage.binary_fill_holes(mask)
    label_im, nb_labels = ndimage.label(mask)
    sizes = ndimage.sum(mask, label_im, range(nb_labels + 1))
    mask_size = sizes < 1800    
    remove_pixel = mask_size[label_im]    
    remove_pixel.shape
    label_im[remove_pixel] = 0
    labels = np.unique(label_im)
    label_im = np.searchsorted(labels, label_im)
    distance = ndimage.distance_transform_edt(label_im)
    local_maxi = peak_local_max(distance, indices=False, footprint=np.ones((80, 80)),labels=label_im)
    markers,cells = ndimage.label(local_maxi)
    labels_watershed = watershed(-distance, markers, mask=label_im)
    print(cd30_image_object.get_id() + ": " + str(cells))
    plt.axis('off')
    plt.subplot(133)
    plt.imshow(labels_watershed, interpolation='nearest') 
    plt.tight_layout()
    plt.title(cd30_image_object.get_id())
    plt.show()
    measurer = ms.Measurer()
    measurer.measure_objects(labels_watershed,cells)
    measurer.write_measurements(arguments["tmp"]+cd30_image_object.get_id()+"_cells.csv")
    