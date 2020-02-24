# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 14:09:25 2018

@author: ben
"""
from interfaces.segmenter_interface import Segmenter
from skimage.filters import threshold_sauvola
from skimage.morphology import watershed
from skimage.feature import peak_local_max
import scipy.ndimage as ndi
import cv2
import numpy as np

class Nuclator(Segmenter):
    
    def __init__(self):
        super().__init__()
        pass
    
    def sauv_thres(self, im, win=39):
        """Apply Sauvola thresholding to greyscale image
        
        Arguments:
            
        im -- greyscale image with nucleus intensities
        
        Keyword arguments:
            
        win -- spatial window size for which threshold is computed (default 39)
        """
        thres = threshold_sauvola(im, window_size=win)
        return im > thres
        
    def segment(self, im, mask_im=None, thresholding_function=self.sauv_thres, nucleus_threshold=200, nucleus_upper_thres=2000, do_label=True):
        """Segment image with subsequent watershed segmentation.
        Optionally apply watershed transform to retrieve separated labeled
        objects.
        
        Arguments:
            
        im -- multichannel input image
        
        Keyword arguments:
            
        thresholding_function -- normally sauvola thresholding default (self.sauv_thres)
        nucleus_threshold -- lower threshold for nucleus size (default 200)
        nucleus_upper_thres -- upper threshold for nucleus size (default 2000)
        do_label -- return labeled image and num labels (default False)
        """
        filtered = cv2.bilateralFilter(im, 15, 25, 15)
        hem_f = filtered[:,:,0]
        nuc_im = thresholding_function(hem_f)
        lbl, num = self.apply_watershed(nuc_im)
        if (do_label):
            return lbl, num
        else:
            return (lbl > 0)
        
    def apply_watershed(self, seg_im):
        """Apply watershed transform to segmented image
        
        Arguments:
        
        seg_im -- binary segmented image
        """
        distance = ndi.distance_transform_edt(seg_im)
        local_maxi = peak_local_max(distance, indices=False, footprint=np.ones((3, 3)), labels=nuc_im)
        markers, num_markers = ndi.label(local_maxi)
        nuc_lbl = watershed(-distance, markers, mask=seg_im)
        return nuc_lbl, num_markers