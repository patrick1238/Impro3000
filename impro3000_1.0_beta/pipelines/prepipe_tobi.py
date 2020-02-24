
# import sys
# import os
# import scipy

# def main(image_object, arguments, library_path):

# 	library_path = library_path
# 	sys.path.append(library_path)
# 	#print("######################## pipeline path: ", library_path)
# 	#save_as_tiff = __import__("save_as_tiff")
	
	
# 	color_deconvolution = __import__("color_deconvolution")
# 	cd30_image_object, hematoxilin_image_object = color_deconvolution.colour_deconvolution(image_object)
# 	#scipy.misc.imsave("E:/Users/Hodgkin/Desktop/develop/impro3000/branches/impro3000_1.0_beta/workspace3000/layer0/tmp/test_"+cd30_image_object.get_id()+".tif", cd30_image_object.get_numpy_array())

# 	print("-- importing module --")
# 	from CellDetector import CellDetector 
# 	cell_detector = CellDetector(arguments)
# 	cell_detector.segment_tile(cd30_image_object, hematoxilin_image_object)


import sys
import os

def main(image_object, arguments, library_path):

	library_path = library_path
	sys.path.append(library_path)
	#print("######################## pipeline path: ", library_path)
	#save_as_tiff = __import__("save_as_tiff")
	
	
	color_deconvolution = __import__("color_deconvolution")
	cd30_image_object, hematoxilin_image_object = color_deconvolution.colour_deconvolution(image_object)
	print("-- importing module --")
	from CellDetector_lib.CellDetector2 import CellDetector 
	#cell_detector = CellDetector(library_path)
	cell_detector = CellDetector(library_path, arguments)
	cell_detector.segment_tile(cd30_image_object, hematoxilin_image_object)
