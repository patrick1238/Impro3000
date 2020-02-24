# -*- coding: utf-8 -*-
"""
Created on Sat Sep 15 18:11:25 2018

@author: ben
"""


import sys
sys.path.append("../imaging_lib/")
#from morphology import Morphologist
from membranator import Membranator
from measure import Measurer
from scipy import misc
#from imaging_lib.nucleaotor import Nucleator

import pandas as pd

class CellDetector():
    
    arguments = {}
    
    def __init__(self,library_path,arguments):
        self.arguments = arguments
        self.library_path = library_path + "/"
        self.cnn_path, self.svm_path, self.scaler_path, self.norm_vec_path, self.out_path = self.__get_paths_from_config(self.library_path + 'cd_config.txt')
        self.segmenter = Membranator(self.library_path + self.cnn_path, self.library_path + self.svm_path, self.library_path + self.scaler_path, self.library_path + self.norm_vec_path)
        self.measurer = Measurer()
        print("done with init")

    def __get_paths_from_config(self, config_file): #='cd_config.txt'):
        cpath_id = 'cnn_path'
        spath_id = 'svm_path'
        scpath_id = 'scaler_path'
        npath_id = 'norm_vec_path'
        out_path_id = 'out_path'        
        cfg = open(config_file, 'r')
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
                if (path_id == cpath_id):
                    cpath = path
                elif (path_id == spath_id):
                    spath = path
                elif (path_id == scpath_id):
                    scpath = path
                elif (path_id == npath_id):
                    npath = path
                elif (path_id == out_path_id):
                    out_path = path
                else:
                    print('Unknown config found ' + line + ' is not known by this class')
        return cpath, spath, scpath, npath, out_path
    


    def segment_tile(self, cd30_tile,hem_tile):
        hem_channel = hem_tile.get_numpy_array()
        cd30_channel = cd30_tile.get_numpy_array()
        #misc.imsave(self.arguments["tmp"] + cd30_tile.get_id()+"_cd30.png",cd30_channel)
        #misc.imsave(self.arguments["tmp"] + cd30_tile.get_id()+"_hematox.png",hem_channel)
        segmented = self.segmenter.segment(hem_channel, cd30_channel)
        #misc.imsave(self.arguments["tmp"] + cd30_tile.get_id()+"_test.png",segmented)
        self.measurer.measure_objects(segmented, im_coords=[cd30_tile.get_global_x(), cd30_tile.get_global_y()])
        self.measurer.write_measurements(self.arguments["cellobjects"]+cd30_tile.get_id()+".csv")
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