# -*- coding: utf-8 -*-
"""
Created on Sat Sep 15 18:11:25 2018

@author: ben
"""


import sys
sys.path.append("../reader/")
sys.path.append("../imaging_lib/")
import os
from os.path import join
#from morphology import Morphologist
from CellDetector_lib.membranator import Membranator
#from imaging_lib.nucleaotor import Nucleator
from CellDetector_lib.measure import Measurer
import pandas as pd
from scipy import misc

class CellDetector():
    
    cpath_id = 'cnn_path'
    spath_id = 'svm_path'
    scpath_id = 'scaler_path'
    npath_id = 'norm_vec_path'
    out_path_id = 'out_path'
    arguments = None
    
    def __init__(self,arguments):
        #self.library_path = library_path + "/"
        #self.cnn_path, self.svm_path, self.scaler_path, self.norm_vec_path, self.out_path = self.__get_paths_from_config(self.library_path + 'cd_config.txt')
        #self.segmenter = Membranator(self.library_path + self.cnn_path, self.library_path + self.svm_path, self.library_path + self.scaler_path, self.library_path + self.norm_vec_path)
        self.arguments = arguments
        self.cnn_path, self.svm_path, self.scaler_path, self.norm_vec_path, self.out_path = self.__get_paths_from_config()
        self.segmenter = Membranator(self.cnn_path, self.svm_path, self.scaler_path, self.norm_vec_path)
        self.segmenter.do_rescale()
        self.measurer = Measurer()
        print("done with init")

    def __get_paths_from_config(self, config_file ='CellDetector_lib/cd_config.txt', no_svm=False):
        lib_folder = os.path.dirname(os.path.abspath(__file__))
        config_path = join(lib_folder, config_file)
        print('path to config is ' + config_path)
        cfg = open(config_path, 'r')
        cpath = ''
        spath = ''
        scpath = ''
        npath = ''
        out_path = ''        
        for line in cfg.readlines():
            if ('=' in line):
                path_arr = line.split('=')
                path_id = path_arr[0].strip()
                path = path_arr[1].strip()
                if (path_id == self.cpath_id):
                    cpath = path
                    cpath = join(lib_folder, path)
                elif (path_id == self.spath_id):
                    spath = path
                    spath = join(lib_folder, spath)
                elif (path_id == self.scpath_id):
                    scpath = path
                    scpath = join(lib_folder, scpath)
                elif (path_id == self.npath_id):
                    npath = path
                    npath = join(lib_folder, npath)
                elif (path_id == self.out_path_id):
                    out_path = path
                else:
                    print('Unknown config found ' + line + ' is not known by this class')
        if no_svm:
            return cpath, None, None, npath, out_path
        else:
            return cpath, spath, scpath, npath, out_path

    def set_outpath(self, setpath):
        self.out_path = setpath
        return

    def print_hi(self):
        print("hi")

    def segment_tile(self, cd30_tile,hem_tile, return_segmented=False):
        hem_channel = hem_tile.get_numpy_array()
        cd30_channel = cd30_tile.get_numpy_array()
        segmented = self.segmenter.segment(cd30_channel, hem_channel)
        if cd30_tile.get_global_x() is None or cd30_tile.get_global_y() is None:
            self.measurer.measure_objects(segmented, im_coords=[0,0])
            self.measurer.write_measurements(self.arguments["cellobjects"]+cd30_tile.get_id()+".csv")
        else:
            self.measurer.measure_objects(segmented, im_coords=[cd30_tile.get_global_x(), cd30_tile.get_global_y()])
            self.measurer.write_measurements(self.arguments["cellobjects"]+cd30_tile.get_id()+".csv")
            
        if return_segmented:
            return segmented
        else:
            return
    
    def write_table(self, out_path, table_format='.csv'):
        table = self.measurer.get_table()
        if (not (table_format in out_path)):
            out_path = out_path[:out_path.index('.')] + table_format
        
        if (table_format == '.csv'):
            table.to_csv(out_path)
        return
        
        
        
'''

Config file example:

cnn_path=u-net_e18.hdf5
svm_path=tissue_detection_svm.pkl
scaler_path=tissue_detection_scaler.pkl
norm_vec_path=im_mean_std_at3.txt
out_path=results/

'''        
        

'''
import argparse
parser = argparse.ArgumentParser('Segment images in folders')
parser.add_argument('--hempath', type=str, help='set the parser for the hematoxylin channel image folder', dest=hempath)
parser.add_argument('--cd30path', type=str, help='set the parser for the CD30 channel image folder', dest=cdpath)
parser.add_argument('--measure', type=bool, help='should segmented objects be measured on the fly?', dest=do_mes)
parser.add_argument('--postprocess', type=str, help='measure segmented objects in this folder', dest=do_post)
parser.add_argument('--dest', type=str, help='name of the folder or file were results should be saved', dest=out_folder)
parser.add_argument('--nuclei', type=bool, help='also segment nuclei', dest=do_nuclei)
parser.add_argument('--svs', type=str, help='specify svs id, hempath and cd30 path are not necessary then', default=None, dest=svs)
if not ()
'''
