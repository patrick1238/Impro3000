# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 14:34:49 2019

@author: patri
"""

import sys
import os
sys.path.append("..")
stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')
from sklearn.externals import joblib
from keras.models import load_model
from keras import backend as K
import numpy as np
from scipy import misc
import gc
from numpy.lib.stride_tricks import as_strided
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
sys.stderr = stderr

def load_ml_dependend_features(config):
    features = {}
    features["sub_size"] = int(config.get("sub_size"))
    features["stepfactor"] = float(config.get("stepfactor"))
    features["stepsize"] = int(features["sub_size"] * features["stepfactor"])
    features["tile_size"] = int(config.get("tile_size"))
    features["offset"] = features["tile_size"] - ((features["tile_size"] // features["stepsize"]) * features["stepsize"])
    features["cnn"] = load_model(os.path.abspath("../"+config.get("cnn_path")))
    features["svm"] = joblib.load(os.path.abspath("../"+config.get("svm_path")))
    features["scaler"] =joblib.load(os.path.abspath("../"+config.get("scaler_path")))
    features["nn_input_size"] = int(config.get("nn_input_size"))
    vec = np.loadtxt(os.path.abspath("../"+config.get("norm_vec_path")))
    features["im_mean"] = vec[:3]
    features["mean_image"] = np.ones((features["sub_size"]//2, features["sub_size"]//2, 3), dtype=np.float32) * features["im_mean"]
    features["im_std"] = vec[3]
    features["tissue_classes"]=config.get("tissue_classes").split(",")
    return features

def resize_patch(patch, yfactor=2, xfactor=2):
    r, c = patch.shape
    rs, cs = patch.strides
    out = as_strided(patch, (r, yfactor, c, xfactor), (rs, 0, cs, 0))
    return out.reshape(r*yfactor, c*xfactor)

def get_features(sub_im, hem=0, cd30=2):
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

def single_cnn_segment(predicted_images, tissue_indices,features): # old impro tile size 3072 -> 3328 ergibt sich daraus
    """Use the CNN to segment cells in the image.
    Returns a segmentation for all tiles where the svm predicted tissue.

    Arguments:
    
    im_tens -- image tensor with shape num x width x height x 3
    tissue_indices -- indices where the svm found expression
    """
    out_im = np.zeros((features["im_size"], features["im_size"]))
    index = 0
    inner_index = 0
    for i in range(0, features["im_size"], features["stepsize"]):
        for k in range(0, features["im_size"], features["stepsize"]):
            if (len(tissue_indices) > 0):
                if (index == tissue_indices[0]):
                    tissue_indices.pop(0)
                    sub_out = predicted_images[inner_index]
                    inner_index += 1
                    sub_out = resize_patch(sub_out)
                    if (k == (features["im_size"] - features["offset"])):
                        if (i == (features["im_size"] - features["offset"])):
                            out_im[i:i + features["offset"], k:k + features["offset"]] += sub_out[:features["offset"],:features["offset"]] * (out_im[i:i + features["offset"],k:k + features["offset"]] == 0)
                        else:
                            out_im[i:i + features["sub_size"], k:k + features["offset"]] += sub_out[:, :features["offset"]] * (
                                    out_im[i:i + features["sub_size"], k:k + features["offset"]] == 0)
                    elif (i == (features["im_size"] - features["offset"])):
                        out_im[i:i + features["offset"], k:k + features["sub_size"]] += sub_out[:features["offset"], :] * (
                            out_im[i:i + features["offset"], k:k + features["sub_size"]] == 0)
                    else:
                        out_im[i:i + features["sub_size"], k:k + features["sub_size"]] += sub_out * (
                            out_im[i:i + features["sub_size"], k:k + features["sub_size"]] == 0)
                index += 1
    return out_im

def make_tensor_apply_svm(im,features):
    """Create the normalized tensor from the image and detect tissue with the SVM
       Input should have hematoxylin intensity at channel 0 and CD30 intensity
       at channel 2.
       
       Arguments:
       im -- multichannel image
    """
    features["im_size"] = im.shape[0]
    tissue_indices = []
    predicted_ims = []
    index = 0
    for i in range(0, features["im_size"], features["stepsize"]):
        for k in range(0, features["im_size"], features["stepsize"]):
            sub_im = np.zeros((features["nn_input_size"], features["nn_input_size"], 3), dtype=np.float32)
            im_part = np.copy(im[i:i + features["sub_size"], k:k + features["sub_size"], :])
            sub = misc.imresize(im_part, 0.5).astype(np.float64)#(0,0), fx=0.5, fy=0.5).astype(np.float64)
            feats = features["scaler"].transform(get_features(sub.astype(np.uint8)))
            expresses = features["svm"].predict(feats) == 1
            if expresses:
                tissue_indices.append(index)
                sub_im[:sub.shape[0], :sub.shape[1], :] = sub / 255.
                sub_im = (sub_im - features["mean_image"]) / features["im_std"]
                sub_im = sub_im[np.newaxis,:]
                predicted_im = features["cnn"].predict(sub_im)
                seg_im = np.argmax(predicted_im, axis=3)
                seg_im = np.squeeze(seg_im)
                predicted_ims.append(seg_im)
            index += 1
    cnn = None
    K.clear_session()
    gc.collect()
    return predicted_ims, tissue_indices    
    
def segment(prim_im,sec_im,config):
    """Segment CD30 membranes in an input image       
        Arguments:
            
        prim_im -- hematoxylin greyscale image
        sec_im -- CD30 greyscale image
    """      
    features = load_ml_dependend_features(config)
    size = prim_im.get_numpy_array().shape[0]
    multi_channel_im = np.zeros((size, size, 3))
    multi_channel_im[:,:,0] = np.copy(sec_im.get_numpy_array())
    multi_channel_im[:,:,2] = np.copy(prim_im.get_numpy_array())
    tensor, tissue_indices = make_tensor_apply_svm(multi_channel_im,features)
    seg_im = single_cnn_segment(tensor, tissue_indices,features)
    return seg_im