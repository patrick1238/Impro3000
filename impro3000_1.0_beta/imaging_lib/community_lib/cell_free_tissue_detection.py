"""
Module to determine the eosinophilic regions of the current image.
Detected regions are saved to disk as binary image, layer 3.
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



def get_roi_from_tmp(arguments):
	""" loads roi and returns it as ndarray """
	roi_tif = Image.open(arguments["tmp"]+"ROI.tif")
	roi_numpy = np.array(roi_tif)
	return roi_numpy


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



	
def get_eosinophilic_regions(arguments, hematox_image_object, roi_numpy, masked_hematox):
	""" function deploys all the threshholding methods. 
		result is a binary image, layer 3, with all detected eosinophilic regions. 
		result is saved to disk."""



	# create initial ndarray masked with roi
	masked_numpy_input = real_np_mask_with_roi(hematox_image_object, roi_numpy)
	masked_numpy_tmp = copy.deepcopy(masked_numpy_input)
	tmp_mask = ma.getmaskarray(masked_numpy_input)

	# apply gaussian filter:
	masked_numpy_gaussian_tmp = scipy.ndimage.filters.gaussian_filter(masked_numpy_input, 0.2)
	masked_numpy_gaussian = ma.masked_array(masked_numpy_gaussian_tmp, mask=tmp_mask)


	# shift intensity values by log2:
	# with gaussian:
	# masked_numpy = masked_numpy_gaussian
	# without gaussian
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


	# get histograms:
	#histogram__orig = cv.calcHist([masked_numpy_tmp], [0], roi_numpy,[256],[0,256])	
	#histogram__shift = cv.calcHist([masked_numpy], [0], roi_numpy,[256],[0,256])


	# threshholding with fixed value:
	ret10,thresh_binnary_shift = cv.threshold(masked_numpy,200,255,cv.THRESH_BINARY)

	
	# perform binary closing:
	hematox_shift_close = scipy.ndimage.morphology.binary_closing(thresh_binnary_shift,  iterations=2)


	# appply maximum filter:
	hematox_maximum = scipy.ndimage.maximum_filter(hematox_shift_close, size=3)


	# SAVE AS IMAGE:
	save_numpy_tmp = np.array(hematox_maximum)
	
	save_numpy_tmp = save_numpy_tmp.astype("uint8")
	save_numpy_tmp[save_numpy_tmp == 1] = 255
	save_numpy = np.ma.filled(save_numpy_tmp, fill_value=0)
	misc.imsave(arguments["results"]+"cell_free_binary.tif",save_numpy)
	



def main(hematox_image_object, arguments):
	""" main method, essentially calls get_eosinophilic_regions, where all logic is in. """
	print("main of detct damn tissue")
	roi_numpy = get_roi_from_tmp(arguments)
	reversed_hematox = mask_numpy_with_roi(hematox_image_object, roi_numpy)
	get_eosinophilic_regions(arguments, hematox_image_object, roi_numpy, reversed_hematox)



if __name__ == '__main__':
	main(hematox_image_object, arguments)











