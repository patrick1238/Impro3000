"""
Module to determine the eosinophilic regions of the current image.
output: binary image, eosinophilic regions are represented black, backgroundtissue is black.
(currently no interchange is possible between pre- and postprocessing pipeline)

@author: Henrik Gollek

"""

import cv2 as cv
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import numpy.ma as ma
import skimage
import scipy
import copy
from scipy import misc
from tqdm import tqdm
import sys
sys.path.append("..")
from imaging import WSI
from imaging import color_deconvolution
from imaging import roi_detector




def mask_numpy_with_roi(hematox_image_object, roi_numpy):
	""" masks the input image with the roi. 
		returns a masked ndarray, all non-roi pixel are made inaccessible. """
	hematox_numpy = hematox_image_object.get_numpy_array()
	reverse_roi_numpy = (255- roi_numpy)
	mask = (reverse_roi_numpy == 0)
	new_array = np.copy(reverse_roi_numpy)
	new_array[mask] = hematox_numpy[mask]
	return new_array


def real_np_mask_with_roi(hematox_image_object, roi_numpy):
	""" different approach to the mask_numpy_with_roi function. similar result. 
		difference: masked pixel have value 0 """
	# creating numpy mask:
	hematox_numpy = hematox_image_object.get_numpy_array()
	# create roi mask -> cast 255 to 1
	reverse_mask = roi_numpy
	reverse_mask[reverse_mask == 255] = 1
	mask = (1 - reverse_mask)
	masked_array = ma.masked_array(hematox_numpy, mask)
	return masked_array



	
def get_eosinophilic_regions(hematox_image_object, roi_numpy, masked_hematox):
	""" function deploys all the threshholding methods. 
		result is a binary image, layer 3, with all detected eosinophilic regions. 
		output: binary ndarray."""


	# create initial ndarray masked with roi
	masked_numpy_input = real_np_mask_with_roi(hematox_image_object, roi_numpy)
	masked_numpy_tmp = copy.deepcopy(masked_numpy_input)
	tmp_mask = ma.getmaskarray(masked_numpy_input)


	# shift intensity values by log2:
	print("-- normalizing with log2, this takes a while --")
	masked_numpy = masked_numpy_input
	for y in range(0,masked_numpy.shape[0],1):
		for x in range(0, masked_numpy.shape[1], 1):
			if not tmp_mask[y,x]:
				val = np.log2(masked_numpy[y,x]+1)
				val = int(val)
				masked_numpy[y,x] = val


	# normalize intensity values:
	print("-- shifting, this takes a while longer - nothing is broken --")
	min_val = np.min(masked_numpy)
	max_val = np.max(masked_numpy)
	for y in range(0,masked_numpy.shape[0],1):
		for x in range(0, masked_numpy.shape[1], 1):
			masked_numpy[y,x]  = ((masked_numpy[y,x] - min_val)/(max_val - min_val)) * 255

	# threshholding with fixed value:
	ret10,thresh_binnary_shift = cv.threshold(masked_numpy,200,255,cv.THRESH_BINARY)	
	# perform binary closing:
	hematox_shift_close = scipy.ndimage.morphology.binary_closing(thresh_binnary_shift,  iterations=2)
	# appply maximum filter:
	hematox_maximum = scipy.ndimage.maximum_filter(hematox_shift_close, size=3)

	# transform ndarray:
	save_numpy_tmp = np.array(hematox_maximum)	
	save_numpy_tmp = save_numpy_tmp.astype("uint8")
	save_numpy_tmp[save_numpy_tmp == 1] = 255
	binary_numpy = np.ma.filled(save_numpy_tmp, fill_value=0)
	return binary_numpy
	
	


########################################### MAIN ###############################################


def get_cellfree_layer(arguments):
	""" main method, essentially calls get_eosinophilic_regions, where all logic is in. """
	print("main of detct damn tissue")
	
	wsi_object = WSI.WSI(arguments["input_path"])
	layer_3 = wsi_object.get_RGB_numpy_array(layer=3)
	roi_numpy = roi_detector.detect_roi(layer_3)

	cd_30_image_object, hematox_image_object = color_deconvolution.colour_deconvolution(layer_3)
	del cd_30_image_object

	
	reversed_hematox = mask_numpy_with_roi(hematox_image_object, roi_numpy)
	binaray_numpy = get_eosinophilic_regions(hematox_image_object, roi_numpy, reversed_hematox)
	return binaray_numpy



i










