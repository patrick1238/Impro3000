# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 14:28:12 2018

@author: bhaladik
"""
import sys
import numpy as np
import cv2
from os.path import join, isfile, isdir
from os import listdir
import argparse

from keras.models import Model, load_model
from keras.layers import Input, concatenate, Conv2D, MaxPooling2D, Activation, UpSampling2D, BatchNormalization
#sys.path.insert(0, 'D:/old_stuff/new_stuff/impro3000-code/branches/impro3000_1.0_beta/imaging_lib')
sys.path.append("..")
import imaging_lib.color_deconvolution as cd
import imaging_lib.ImageObject as im_o
import imaging_lib.CellDetector_lib.membranator as memba
import scipy.ndimage as ndi
import imaging_lib.CellDetector as cDetect



def perform_segmentation(in_folder, out_folder):
    print(in_folder)
    im_names = [f for f in listdir(in_folder) if ('.tif' in f)]
    #model = load_model(model_path)
    print(im_names)
    for name in im_names:
        path = join(in_folder, name)
        print('processing ' + name)
        im_orig = cv2.imread(path)
        im_object = im_o.ImageObject(objectID=name.replace(".tif",""),numpy_array = cv2.cvtColor(im_orig, cv2.COLOR_BGR2RGB))
        cd_im, hem = cd.colour_deconvolution(im_object)
        #cd_im = cd_im.get_numpy_array()
        #hem = hem.get_numpy_array()
        arguments = {}
        arguments["cellobjects"] = out_folder
        arguments["tmp"] = out_folder
        detector = cDetect.CellDetector(arguments)
        detector.set_outpath(out_folder)
        seg = detector.segment_tile(cd_im, hem, return_segmented=True)
        print('shape of segmented image is')
        print(seg.shape)
        seg = (seg == 1) + (seg == 2) + (seg == 3)
        seg = ndi.morphology.binary_fill_holes(seg)
        out_seg = np.zeros(seg.shape, dtype=np.uint8)
        print('shape of out seg is')
        print(out_seg.shape)
        lbl, num = ndi.label(seg)
        for i in range(1, num+1):
            if (np.sum(lbl == i) >= 1200):
                out_seg += (lbl == i)
        inv_im = (np.ones(out_seg.shape, dtype=np.uint8) - out_seg)# * 100
        print('printing sums')
        print(np.sum(seg))
        print(np.sum(out_seg))
        print(np.sum(inv_im))
        vis = np.zeros(im_orig.shape, dtype=np.float32)
        for i in range(im_orig.shape[2]):
            vis[:,:,i] = (im_orig[:,:,i].astype(np.float32) * out_seg.astype(np.float32)) + ((inv_im.astype(np.float32) * 0.5) * im_orig[:,:,i].astype(np.float32))
        out = np.clip(vis.astype(np.uint8), 0, 255)
        print('writing image to ' + join(out_folder, name))
        cv2.imwrite(join(out_folder, name), out.astype(np.uint8))


if __name__ == '__main__':
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('model', type=str, help='path to model for segmentation', default='u-net_gen_newaug_e24.hdf5')
    parser.add_argument('target', type=str, help='folder of images to segment', default='../test_files/image/tiled_layer0')
    parser.add_argument('out', type=str, help='folder to write to', default='../test/workspace3000/')
    parser.add_argument('colordeconvolution', type=str, help='path to color deconvolution file', default='color_deconvolution_lib/cd30_hematoxylin_rest.csv')
    parser.parse_args()
    perform_segmentation(parser.target, parser.out, parser.colordeconvolution)
    """
    perform_segmentation('C:/Users/patri/OneDrive/Dokumente/develop/impro3000/branches/impro3000_1.0_beta/test_files/image/tiled_layer0/','C:/Users/patri/OneDrive/Dokumente/develop/impro3000/branches/impro3000_1.0_beta/workspace3000/test/')
