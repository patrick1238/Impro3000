# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 19:42:11 2019

@author: Carbon
"""
from skimage.measure import regionprops
import scipy.ndimage as ndi
import numpy as np


class NucleiAssigner:
    
    def __init__(self, measurer_object):
        """
        initialize with measurement object to identify membrane nuclei and perform measurements simultanously
        """
        self.measurer = measurer_object
    
    def assign_nuclei_to_membranes(self, membrane_segmentation, nucleus_segmentation, by_area=True, by_center=True, nucleus_threshold=150, im_coords=[0,0]):
        """
        Function to assign segmented nuclei to membranes.
        Returns:
        out_mask: integer matrix with same shape as input matrix, containing the nuclei
        out_mask is binary if no measurer object was passed during initialization
        out_mask contains nuclei with labels from 1 ... num_nuclei if measurer object was given
        
        
        Arguments:
        membrane_segmentation - numpy matrix: segmented image of membranes either binary, or direct output of membranator object
        nucleus_segmentation - numpy matrix: segmented nuclei image - expected to be binary
        
        by_area - boolean: flag that indicates whether nuclei should be returned by their overlap area with membranes
        by_center - boolean: flag that indicates whether nuclei should be returned if their centers are within membranes
        nucleus_threshold - int: size exclusion threshold for nuclei, only applied if by_area is set to True
        
        """
        
        out_mask = np.zeros((membrane_segmentation.shape[0], membrane_segmentation.shape[1]), dtype=np.int32)
        membrane_segmentation = (membrane_segmentation == 1) + (membrane_segmentation == 2) + (membrane_segmentation == 3)
        # label nuclei and measure them
        nuc_labeled, num_nucs = ndi.label(nucleus_segmentation)
        nuclei_props = regionprops(nuc_labeled)
        # get labels of nuclei within membranes
        nuclei_ids_in_membranes = np.unique(membrane_segmentation * nuc_labeled) 
        measure_nuc_labels = []
        measure_nuc_centers = []
        measure_nuc_ids = []
        for nuc_obj in nuclei_props:
            y, x = nuc_obj.centroid
            nuc_id = nuc_obj.label
            do_write = False
            # check if center is in membrane
            if by_center:
                if (membrane_segmentation[int(y), int(x)] > 0):
                    do_write = True
            # check if area overlap with membrane is sufficient
            elif by_area:
                if nuc_id in nuclei_ids_in_membranes:
                    nuc_area = np.sum(membrane_segmentation * (nuc_labeled == nuc_id))
                    if (nuc_area  >= nucleus_threshold):
                        do_write = True
            # write nucleus if specified conditiions are fullfilled
            if do_write:
                y1, x1, y2, x2 = nuc_obj.bbox
                if (self.measurer is None):
                    out_mask[y1:y2,x1:x2] = nuc_obj.filled_image
                else:
                    out_mask[y1:y2,x1:x2] = (nuc_obj.filled_image * nuc_id)
                    measure_nuc_labels.append(nuc_id)
                    measure_nuc_centers.append([x,y])
                    measure_nuc_ids.append(nuc_id)
        if not (self.measurer is None):
            print('{} objects are passed to the measurer'.format(len(measure_nuc_centers)))
            self.measurer.measure_objects(out_mask, num_labels=len(measure_nuc_centers), label_list=measure_nuc_labels, input_centers=measure_nuc_centers, im_coords=im_coords)
        return out_mask
    
    def get_measurer(self):
        return self.measurer