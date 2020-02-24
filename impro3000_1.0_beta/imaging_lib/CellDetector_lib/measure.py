# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 14:37:51 2018

@author: ben
"""

import scipy.ndimage as ndi
import numpy as np
import pandas as pd
from os.path import join, isfile
from os import listdir
import cv2
import time
from sklearn.externals import joblib
import sklearn.svm
from sklearn.preprocessing import StandardScaler
#from ImageSegmenter import ImageSegmenter
import skimage.measure as mes
from scipy import spatial
import time
import os

class Measurer:
    CSV_FORMAT = '.csv'
    ident = 'ID'
    coords = 'Coordinates'
    x_coord_id = 'X_Coordinate'
    y_coord_id = 'Y_Coordinate'
    size_id = 'Size'
    circ_id = 'Circumference'
    # contour_id = 'Contour_Profile'
    orientation_id = 'Orientations'
    # edt_id = 'EDT_Descriptor'
    roundness_id = 'Roundness'
    ax_length = 'Major Axis Length'
    # column_names = [ident, coords, size_id, circ_id, eigen_id, roundness_id]
    column_names = [ident, coords, size_id, circ_id, orientation_id, roundness_id]
    micrometers_to_pixels = 0.125
    # contour_profile_length = 100
    im_size = 3072
    segmenter = None

    def __init__(self, lower_threshold=1200, upper_threshold=200000, use_svm=False, svs=None, im_size=3072):
        self.object_sizes = []
        self.coordinates = []
        self.circumferences = []
        # self.contour_profiles = []
        self.orientations = []
        self.edt_descriptors = []
        self.roundnesses = []
        self.object_index = 0
        self.lower_thres = lower_threshold
        self.axis_lengths = []
        self.upper_thres = upper_threshold
        #print('lower threshold is ' + str(self.lower_thres))
        
    def measure_objects(self, segmented, num_labels=0, im_coords=[0, 0], current_name=''):
        start = time.time()
        if (num_labels == 0):
            labeled, num_features = ndi.measurements.label(segmented)
        else:
            labeled = segmented
            num_features = num_labels
        object_ids = range(1, num_features + 1)
        #print('found {} objects'.format(num_features))
        border_labels = self.get_border_object_labels(labeled)
        measures = mes.regionprops(labeled)
        out_measures = []
        border_labels = self.get_border_object_labels(labeled)
        for mes_object in measures:
            if (mes_object.filled_area >= self.lower_thres)  and (not (mes_object.label in border_labels) and (mes_object.filled_area <= self.upper_thres)):
                new_x = mes_object.centroid[1] + im_coords[0]
                new_y = mes_object.centroid[0] + im_coords[1]
                self.object_sizes.append(mes_object.filled_area)
                self.coordinates.append([new_x, new_y])
                self.orientations.append(mes_object.orientation)
                fil = mes_object.filled_image
                circumference = np.sum(ndi.morphology.distance_transform_edt(fil) == 1)
                self.circumferences.append(circumference)
                roundness = 4 * np.pi * mes_object.filled_area / (circumference ** 2)
                self.roundnesses.append(roundness)
                self.axis_lengths.append(mes_object.major_axis_length)
                self.object_index += 1
        end = time.time()
        elapsed_minutes = (end - start) / 60.
        print('Measured {} objects after filtering'.format(self.object_index))
        return elapsed_minutes
    
    def get_measurements(self):
        x_coords = [coord[0] for coord in self.coordinates]
        y_coords = [coord[1] for coord in self.coordinates]
        table_dict = {'ID': range(1, self.object_index + 1), self.x_coord_id : x_coords, self.y_coord_id : y_coords, 'Size': self.object_sizes,
                      'Circumference': self.circumferences, 'Roundness': self.roundnesses, 'Orientation' : self.orientations, 'Major Axis Length' : self.axis_lengths}
        table = pd.DataFrame.from_dict(table_dict)
        return table
    
    def write_measurements(self, path):
        table = self.get_measurements()
        if (self.CSV_FORMAT in path):
            table.to_csv(path)
            os.rename(path,path.replace(".csv",".isg"))
        else:
            print("CAN ONLY WRITE CSV FORMAT. THE FILE NEEDS TO END WITH .csv! ABORTING!")
            return
    '''   
    def has_no_duplicate(self, check_coord, coord_list, threshold=20.):
        for coord in coord_list:
            x = coord[0]
            y = coord[1]
            x_check = check_coord[0]
            y_check = check_coord[1]
            dist = np.sqrt((x - x_check) ** 2 + (y - y_check) ** 2)
            if dist < threshold:
                return False
        return True
    '''
    
    def has_no_duplicate(self, check_coord, coord_list, threshold=20., tree=None):
        if (len(coord_list) < 2):
            return True, None
        if (tree is None):
            tree = spatial.KDTree(coord_list)
        dist, index = tree.query(check_coord)
        if dist < threshold:
            return False, tree
        else:
            return True, None
        
        
    def remove_duplicates(self, table, threshold=20.):
        print('using kd tree approach with timer and tree remembering')
        start = time.time()
        removal_indices = []
        checked_coords = []
        index = 0
        tree = None
        for id, row in table.iterrows():
            coord_string = row['Coordinates']
            coord = self.make_float_coord(coord_string)
            is_dup, out_tree = self.has_no_duplicate(coord, checked_coords, tree=tree)
            tree = out_tree
            if is_dup:
                checked_coords.append(coord)
            else:
                removal_indices.append(index)
            index += 1
        print('Removing {} duplicate objects out of {}'.format(len(removal_indices), index))
        table.drop(table.index[removal_indices], inplace=True)
        end = time.time()
        print('removing all duplicates took {} miunutes'.format((end - start) / 60))
        return table
    
    def remove_duplicates_filter_size(self, table, threshold=15.):
        print('using kd tree approach with timer and tree remembering')
        start = time.time()
        removal_indices = []
        checked_coords = []
        index = 0
        tree = None
        num_objects = len(table['Coordinates'])
        multi = 1
        frac = 0.1
        print('performing filtering on ' + str(len(table['Coordinates'])) + ' objects')
        for id, row in table.iterrows():
            coord_string = row['Coordinates']
            size_string = row['Size']
            size = float(size_string)
            coord = self.make_float_coord(coord_string)
            if (size >= self.lower_thres):
                is_dup, out_tree = self.has_no_duplicate(coord, checked_coords, tree=tree)
                tree = out_tree
                if is_dup:
                    checked_coords.append(coord)
                else:
                    removal_indices.append(index)
            else:
                removal_indices.append(index)
            if (index >= (multi * frac * num_objects)):
                print('first ' + str(multi) + ' times ten percent done!')
                multi += 1
            index += 1
        print('Removing {} duplicate objects out of {}'.format(len(removal_indices), index))
        table.drop(table.index[removal_indices], inplace=True)
        end = time.time()
        print('removing all duplicates took {} miunutes'.format((end - start) / 60))
        return table
    
    def make_float_coord(self, coord_string):
        x_string, y_string = coord_string.split(',')
        x = float(x_string[1:])
        y = float(y_string[1:len(y_string) - 1])
        return [x, y]
    
    def measure_folder(self, folder):
        files = [f for f in listdir(folder) if isfile(join(folder, f))]
        tiles_left = len(files)
        max_time = -1
        for f in files:
            name_arr = f[:len(f) - 4].split('_')
            y = int(name_arr[len(name_arr) - 1]) * self.im_size
            x = int(name_arr[len(name_arr) - 2]) * self.im_size
            mask = cv2.imread(join(folder, f), 0)
            minutes = self.measure_objects(mask, im_coords=[x, y])
            if (minutes > max_time):
                max_time = minutes
            tiles_left -= 1
            print('between {} and {} hours left for {} tiles'.format(((max_time * tiles_left) / 60.),
                                                                     ((minutes * tiles_left) / 60.), tiles_left))
            
    def get_border_object_labels(self, labeled):
        lower = np.unique(labeled[labeled.shape[0] - 1, :])
        if (0 in lower):
            lower = lower[1:]
        upper = np.unique(labeled[0, :])
        if (0 in upper):
            upper = upper[1:]
        left = np.unique(labeled[:, 0])
        if (0 in left):
            left = left[1:]
        right = np.unique(labeled[:, labeled.shape[1] - 1])
        if (0 in right):
            right = right[1:]
        whole = np.concatenate((lower, upper, left, right))
        return whole
    
    def get_table(self):
        table_dict = {'ID': range(1, self.object_index + 1), 'Coordinates': self.coordinates, 'Size': self.object_sizes,
                      'Circumference': self.circumferences, 'Roundness': self.roundnesses, 'Orientation' : self.orientations, 'Major Axis Length' : self.axis_lengths}
        table = pd.DataFrame.from_dict(table_dict)
        return table