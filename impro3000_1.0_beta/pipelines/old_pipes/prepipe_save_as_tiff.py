
import sys
import os

def main(image_object, arguments, library_path):

	library_path = library_path
	sys.path.append(library_path)

	color_deconvolution = __import__("color_deconvolution")
	cd30_image_object, hematoxilin_image_object = color_deconvolution.colour_deconvolution(image_object)
	
	save_as_tiff = __import__("save_as_tiff")
	#save_as_tiff.main(image_object, arguments["tmp"])
	save_as_tiff.main(hematoxilin_image_object, arguments["tmp"])
	

if __name__ == '__main__':
	main(image_object, arguments, library_path)