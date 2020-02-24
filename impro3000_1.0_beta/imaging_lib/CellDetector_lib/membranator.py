# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 13:19:18 2018

@author: ben
"""
import sys
sys.path.append("..")
from sklearn.preprocessing import StandardScaler
from sklearn import svm
from sklearn.externals import joblib
from keras.models import Model, load_model
from keras import backend as K
import numpy as np
from imaging_lib.interfaces.segmenter_interface import Segmenter
import scipy.ndimage as ndi
import time
import cv2
from skimage.transform import resize
import gc
from numpy.lib.stride_tricks import as_strided

class Membranator(Segmenter):
    sub_size = 256
    tissue_classes = [1,2,3]
    rescale = False
    im_size = 3328
    nn_input_size = 256
    return_raw = True

    def resize_patch(self, patch, yfactor=2, xfactor=2):
        print('shape of input patch is {}'.format(patch.shape))
        r, c = patch.shape
        rs, cs = patch.strides
        out = as_strided(patch, (r, yfactor, c, xfactor), (rs, 0, cs, 0))
        return out.reshape(r*yfactor, c*xfactor)

    def set_return_raw(self, do_raw):
        """
        set the class to raw return. Instead of returning the segmented image as a binary image,
        return the segmented image with the class assignemts: The image will contain numbers from
        0 to 8
        """
        self.return_raw = do_raw

    
    def __init__(self, cnn_path, svm_path, scaler_path, norm_vec_path, step_factor=0.95, out_im_size=3072):
        super().__init__()
        self.cnn_path = cnn_path
        if ((svm_path is None) and (scaler_path is None)):
            self.svm = None
            self.scaler = None
            print('Setting svm and scaler to None')
        else:
            self.svm = joblib.load(svm_path)
            self.scaler =joblib.load(scaler_path)
        self.out_im_size = out_im_size
        self.step_factor = step_factor
        self.stepsize = int(float(self.sub_size) * self.step_factor) # overlap, tile size for
        #print('stepsize is {}'.format(self.stepsize))
        self.offset = self.out_im_size - ((self.out_im_size // self.stepsize) * self.stepsize)
        #print('offset is {}'.format(self.offset))
        vec = np.loadtxt(norm_vec_path)
        self.im_mean = vec[:3]
        self.mean_image = np.ones((self.sub_size, self.sub_size, 3), dtype=np.float32) * self.im_mean
        self.im_std = vec[3]
        self.num_tissue_tiles = 0
        self.im_size = out_im_size
        
        
    def do_rescale(self):
        self.sub_size = 512
        self.rescale = True
        self.stepsize = int(self.sub_size * self.step_factor) # overlap, tile size for 
        self.offset = self.out_im_size - ((self.out_im_size // self.stepsize) * self.stepsize)
        return
        
    def set_im_size(self, size):
        self.im_size = size
        return
    
    def get_features(self, sub_im, hem=0, cd30=2):
        """Compute the features for the svm
        
        Arguments:
            
        sub_im -- 256x256 image
        
        Keyword arguments:
        hem -- index of hematoxylin channel (default 0)
        cd30 -- index of CD30 channel (default 2)
        """
        features = np.zeros((1, 4), dtype=np.float32)
        features[:, 0] = np.sum(sub_im[:, :, hem])
        features[:, 1] = np.sum(sub_im[:, :, cd30])
        features[:, 2] = np.std(sub_im[:, :, hem])
        features[:, 3] = np.mean(sub_im[:, :, hem])
        return features
    
    
    def single_cnn_segment(self, predicted_images, tissue_indices): # old impro tile size 3072 -> 3328 ergibt sich daraus
        """Use the CNN to segment cells in the image.
        Returns a segmentation for all tiles where the svm predicted tissue.
        
        Arguments:
        
        im_tens -- image tensor with shape num x width x height x 3
        tissue_indices -- indices where the svm found expression
        """
        print('starting to predict single image')
        start_single = time.time()
        out_im = np.zeros((self.im_size, self.im_size))
        #prediction_tensor = self.cnn.predict(im_tens) # takes very long
        index = 0
        inner_index = 0
        for i in range(0, self.im_size, self.stepsize):
            for k in range(0, self.im_size, self.stepsize):
                #print('working at steps i {} and k {}'.format(i,k))
                if (len(tissue_indices) > 0):
                    if (index == tissue_indices[0]):
                        tissue_indices.pop(0)
                        #sub_tensor = prediction_tensor[inner_index]
                        
                        #sub_out = np.argmax(sub_tensor, axis=2)
                        sub_out = predicted_images[inner_index]
                        inner_index += 1
                        if (self.rescale):
                            #sub_out = resize(sub_out, (self.sub_size, self.sub_size), preserve_range=True)
                            sub_out = self.resize_patch(sub_out)
                            #print('sub out has shape {}'.format(sub_out.shape))
                        if (k == (self.im_size - self.offset)):
                            if (i == (self.im_size - self.offset)):
                                out_im[i:i + self.offset, k:k + self.offset] += sub_out[:self.offset,
                                                                                :self.offset] * (
                                                                                    out_im[
                                                                                    i:i + self.offset,
                                                                                    k:k + self.offset] == 0)
                            else:
                                out_im[i:i + self.sub_size, k:k + self.offset] += sub_out[:, :self.offset] * (
                                    out_im[i:i + self.sub_size, k:k + self.offset] == 0)
                        elif (i == (self.im_size - self.offset)):
                            out_im[i:i + self.offset, k:k + self.sub_size] += sub_out[:self.offset, :] * (
                                out_im[i:i + self.offset, k:k + self.sub_size] == 0)
                        else:
                            out_im[i:i + self.sub_size, k:k + self.sub_size] += sub_out * (
                                out_im[i:i + self.sub_size, k:k + self.sub_size] == 0)
                index += 1
        end_single = time.time()
        time_minutes = (end_single - start_single) / 60
        """
        if (np.sum(out_im > 0)):
                print('predicted image is not empty!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                print('sum is {}'.format(np.sum(out_im)))
                print('Unique values are {}'.format(np.unique(out_im)))
        """
        print('created segmented image. This took {}m'.format(time_minutes))
        return out_im, time_minutes
    
    def make_tensor_apply_svm(self, im):
        """Create the normalized tensor from the image and detect tissue with the SVM
        Input should have hematoxylin intensity at channel 0 and CD30 intensity
        at channel 2.
        
        Arguments:
        im -- multichannel image
        """
        
        im_size = im.shape[0]
        ims = []
        tissue_indices = []
        predicted_ims = []
        index = 0
        self.cnn = load_model(self.cnn_path)
        for i in range(0, im_size, self.stepsize):
            for k in range(0, im_size, self.stepsize):
                sub_im = np.zeros((self.nn_input_size, self.nn_input_size, 3), dtype=np.float32)
                if self.rescale:
                    im_part = np.copy(im[i:i + self.sub_size, k:k + self.sub_size, :])
                    sub = cv2.resize(im_part, (0,0), fx=0.5, fy=0.5).astype(np.float64)
                else:
                    sub = np.copy(im[i:i + self.sub_size, k:k + self.sub_size, :]).astype(np.float64)
                if ((self.scaler is None) or (self.svm is None)):
                    tissue_indices.append(index)
                    sub_im[:sub.shape[0], :sub.shape[1], :] = sub / 255.
                    
                    sub_im = (sub_im - self.mean_image) / self.im_std
                    sub_im = sub_im[np.newaxis,:]
                    ## predict image as one piece, to make sure it fits in gpu memory
                    predicted_im = self.cnn.predict(sub_im)
                    seg_im = np.argmax(predicted_im, axis=3)
                    seg_im = np.squeeze(seg_im)
                    predicted_ims.append(seg_im)
                    index += 1
                else:
                    feats = self.scaler.transform(self.get_features(sub.astype(np.uint8)))
                    expresses = self.svm.predict(feats) == 1
                    if expresses:
                        tissue_indices.append(index)
                        sub_im[:sub.shape[0], :sub.shape[1], :] = sub / 255.
                        sub_im = (sub_im - self.mean_image) / self.im_std
                        sub_im = sub_im[np.newaxis,:]
                        predicted_im = self.cnn.predict(sub_im)
                        #print(predicted_im.shape)
                        seg_im = np.argmax(predicted_im, axis=3)
                        seg_im = np.squeeze(seg_im)
                        #print(seg_im.shape)
                        predicted_ims.append(seg_im)
                        #ims.append(sub_im)
                    index += 1
        #im_tens = np.array(ims)
        #print('image tensor has shape {}'.format(im_tens.shape))
        self.num_tissue_tiles += len(tissue_indices)
        #print('{} out of {} subimages contain tissue'.format(len(tissue_indices), 196))
        self.cnn = None
        K.clear_session()
        gc.collect()
        return predicted_ims, tissue_indices
    
    def segment(self, prim_im, sec_im):
        super().segment()
        """Segment CD30 membranes in an input image
        
        Arguments:
            
        prim_im -- hematoxylin greyscale image
        sec_im -- CD30 greyscale image
        """
        if (prim_im.shape != sec_im.shape):
            print('Shapes for primary and secondary channel do not match! \n ABORTING!!')
            return
        if (prim_im.shape[0] != prim_im.shape[1]):
            print('images are not of quadratic shape! \n ABORTING!!!')
        size = prim_im.shape[0]
        multi_channel_im = np.zeros((size, size, 3))
        multi_channel_im[:,:,0] = np.copy(sec_im)
        multi_channel_im[:,:,2] = np.copy(prim_im)
        tensor, tissue_indices = self.make_tensor_apply_svm(multi_channel_im)
        seg_im, time_minutes = self.single_cnn_segment(tensor, tissue_indices)
        if (self.return_raw):
            return seg_im
        else:
            out = np.zeros(seg_im.shape, dtype=np.uint8)
            for i in self.tissue_classes:
                out += ndi.morphology.binary_fill_holes(seg_im == i)
            return out
        
        

        
