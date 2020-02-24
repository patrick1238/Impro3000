
import sys
import os

def main(image_object, arguments, library_path):

	library_path = library_path
	sys.path.append(library_path)
	color_deconvolution = __import__("color_deconvolution")
	cd30,hematoxilin = color_deconvolution.colour_deconvolution(image_object)
	detect_sklerotic_tissue = __import__("detect_sklerotic_tissue")
	detect_sklerotic_tissue.main(hematoxilin, arguments)
	#save_as_tiff = __import__("save_as_tiff")
	#save_as_tiff.main(image_object, arguments["tmp"])
	#detect_sklerotic_tissue.main(image_object, arguments)

	

if __name__ == '__main__':
	main(image_object, output_path, library_path)