# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 15:02:04 2018

@author: ben
"""
from imaging_lib.nucleator import Nucleator
from membranator import Membranator
from measure import Measurer
import cv2

class Morphologist:
    CSV_FORMAT = '.csv'
    ident = 'ID'
    coords = 'Coordinates'
    size_id = 'Size'
    circ_id = 'Circumference'
    orientation_id = 'Orientations'
    roundness_id = 'Roundness'
    ax_length = 'Major Axis Length'
    
    nucleus_lower_threshold = 450
    membrane_lower_threshold = 1800
    
    nucleus_upper_threshold = None
    membrane_upper_threshold = None
    
    
    def __init__(self, do_nuclei=False, cnn_path='u-net_e18.hdf5',
                 svm_path='tissue_detection_svm.pkl',
                 scaler_path='tissue_detection_scaler.svm',
                 normalization_vector_path='im_mean_std_at3.txt', postprocessing_path=None):
        if (postprocessing_path is None):
            self.post_path = None
            self.membranator = Membranator(cnn_path, svm_path, scaler_path, normalization_vector_path)
            self.measurer_membranes = Measurer(lower_threshold=self.membrane_lower_threshold, upper_threshold=None)
            if do_nuclei:
                self.nucleator = Nucleator()
                self.measurer_nuclei = Measurer(lower_threshold=self.nucleus_lower_threshold, upper_threshold=self.nucleus_upper_threshold)
        else:
            self.post_path = postprocessing_path
            if do_nuclei:
                self.measurer_nuclei = Measurer(lower_threshold=self.nucleus_lower_threshold, upper_threshold=self.nucleus_upper_threshold)
            else:
                self.measurer_membranes = Measurer(lower_threshold=self.membrane_lower_threshold, upper_threshold=None)
                
    def postprocess_folder(self):
        if (self.post_path is None):
            print('No path for postprocessing given. ABORTING!!')
            return
        else:
            if self.do_nuclei:
                self.measurer_nuclei.process_folder(self.post_path)
                table = self.measurer_nuclei.get_table()
                table_post = self.measurer_nuclei.remove_duplicates(table)
                return table_post
            else:
                self.measurer_membranes.process_folder(self.post_path)
                table = self.measurer_membranes.get_table()
                table_post = self.measurer_membranes.remove_duplicates(table)
            return table_post
        
    def measure_image(self, nuclei_image=None, membrane_image=None, coords=[0,0]):
        if not (nuclei_image is None):
            self.measurer_nuclei.measure_objects(nuclei_image, im_coords=coords)
        if not(membrane_image is None):
            self.measurer_membranes.measure_objects(membrane_image, im_coords=coords)
        
                
                
    
                
                
        