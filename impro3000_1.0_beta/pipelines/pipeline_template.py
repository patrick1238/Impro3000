# adding path to Imaging_Library to sys path in order to easely import modules not located in the svs_reade dir:
import sys
import os
#sys.path.append("C:/Users/D.Va/OneDrive - direkt gruppe GmbH/AK_Koch/FP/Code/Impro3000/Imaging_Library")

#current_path = os.getcwd()
#print("############# curretn path pipeline: ", current_path)
#sys.path.append("C:/Users/D.Va/OneDrive - direkt gruppe GmbH/AK_Koch/FP/Code/Impro3000/Imaging_Library")

# imports for all modules from the Imaging_Library
#import save_as_tiff



def main(image_object, output_path, library_path):

	library_path = library_path
	sys.path.append(library_path)
	#print("######################## pipeline path: ", library_path)
	save_as_tiff = __import__("save_as_tiff")


	save_as_tiff.main(image_object, output_path)


if __name__ == '__main__':
	main(image_object, output_path, library_path)