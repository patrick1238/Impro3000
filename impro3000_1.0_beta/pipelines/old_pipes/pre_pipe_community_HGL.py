# pre pipe for communities - master final

import sys
import os

def main(image_object, arguments, library_path):

	sys.path.append(library_path)

	# save layer as .tif:
	save_as_tiff = __import__("save_as_tiff")
	save_as_tiff.main(image_object, arguments["results"])

	# color deconvolution:
	color_deconvolution = __import__("color_deconvolution")
	cd30,hematoxilin = color_deconvolution.colour_deconvolution(image_object)

	# detect cell free tissue:
	sys.path.append(library_path + "/community_lib")   
	cell_free_tissue_detection = __import__("cell_free_tissue_detection")
	cell_free_tissue_detection.main(hematoxilin, arguments)
	
	print("[!!] omitting main for test porpouse [!!]")


	
