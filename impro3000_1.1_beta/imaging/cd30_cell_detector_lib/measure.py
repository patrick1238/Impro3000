# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 14:35:40 2019

@author: patri
"""
import scipy.ndimage as ndi
import numpy as np
import pandas as pd
from os.path import join, isfile
from os import listdir
import time
import skimage.measure as mes
from scipy import spatial
import os
import scipy

    
def measure_objects(segmented, num_labels=0, im_coords=[0, 0], current_name='', lower_thres=1600, upper_thres=20000):
    if (num_labels == 0):
        labeled, num_features = ndi.measurements.label(segmented)
    else:
        labeled = segmented
    border_labels = get_border_object_labels(labeled)
    measures = mes.regionprops(labeled,coordinates='xy')
    border_labels = get_border_object_labels(labeled)
    cells = {}
    cell_id = 0
    for mes_object in measures:
        if (mes_object.filled_area >= lower_thres)  and (not (mes_object.label in border_labels) and (mes_object.filled_area <= upper_thres)):
            cell = {}
            new_x = mes_object.centroid[1] + im_coords[0]
            new_y = mes_object.centroid[0] + im_coords[1]
            cell["x"]= new_x
            cell["y"]= new_y
            cell["area"]= mes_object.filled_area
            cell["orientation"] = mes_object.orientation
            cell["circumference"] = np.sum(ndi.morphology.distance_transform_edt(mes_object.filled_image) == 1)
            cell["roundnes"] = 4 * np.pi * mes_object.filled_area / (cell["circumference"] ** 2)
            cell["majoraxislength"] = mes_object.major_axis_length
            cells[cell_id] = cell
            cell_id = cell_id + 1
    return cells

def convert_to_dataframe(cells):
    table_dict = {"ID":[]}
    for cell_id,properties in cells.items():
        table_dict["ID"].append(cell_id)
        for key,value in properties.items():
            if key in table_dict:
                table_dict[key].append(value)
            else:
                table_dict[key] = [value]           
    table = pd.DataFrame.from_dict(table_dict)
    return table

def write_measurements(cells,path):
    table = convert_to_dataframe(cells)
    if ('.csv' in path):
        table.to_csv(path)
        os.rename(path,path.replace(".csv",".isg"))
    else:
        print("CAN ONLY WRITE CSV FORMAT. THE FILE NEEDS TO END WITH .csv! ABORTING!")
        return


def has_no_duplicate(check_coord, coord_list, threshold=20., tree=None):
    if (len(coord_list) < 2):
        return True, None
    if (tree is None):
        tree = spatial.KDTree(coord_list)
    dist, index = tree.query(check_coord)
    if dist < threshold:
        return False, tree
    else:
        return True, None
    
    
def remove_duplicates(table, threshold=20.):
    print('using kd tree approach with timer and tree remembering')
    start = time.time()
    removal_indices = []
    checked_coords = []
    index = 0
    tree = None
    for id, row in table.iterrows():
        coord_string = row['Coordinates']
        coord = make_float_coord(coord_string)
        is_dup, out_tree = has_no_duplicate(coord, checked_coords, tree=tree)
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


def remove_duplicates_filter_size(table, threshold=15., lower_thres=1200):
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
        coord = make_float_coord(coord_string)
        if (size >= lower_thres):
            is_dup, out_tree = has_no_duplicate(coord, checked_coords, tree=tree)
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

def make_float_coord(coord_string):
    x_string, y_string = coord_string.split(',')
    x = float(x_string[1:])
    y = float(y_string[1:len(y_string) - 1])
    return [x, y]

def measure_folder(folder, im_size=3072):
    files = [f for f in listdir(folder) if isfile(join(folder, f))]
    tiles_left = len(files)
    max_time = -1
    for f in files:
        name_arr = f[:len(f) - 4].split('_')
        y = int(name_arr[len(name_arr) - 1]) * im_size
        x = int(name_arr[len(name_arr) - 2]) * im_size
        mask = scipy.misc.imread(join(folder, f), 0)
        minutes = measure_objects(mask, im_coords=[x, y])
        if (minutes > max_time):
            max_time = minutes
        tiles_left -= 1
        print('between {} and {} hours left for {} tiles'.format(((max_time * tiles_left) / 60.),
                                                                 ((minutes * tiles_left) / 60.), tiles_left))
        
def get_border_object_labels(labeled):
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



