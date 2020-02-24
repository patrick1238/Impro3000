# -*- coding: utf-8 -*-
"""
The call pipeline module is in it's logic actaully part of the svs_reader.py. 
As it is impossible to start more than one jvm within one Python process, instead call parallel is 
being called several times - hence the name - from the svs_reader.py.

The module serves two purposes:
1. starting a jvm in which a sublist of image tiles is processed (not exactly paralleization, but as close as we could get)
2. importing a pipeline, that serves as a connection to the Imaging Library and its modules. 

All modules defined in the pipeline are excecuted on each tile.
"""
import bioformats as bf
import javabridge as jv
import numpy as np

import os
import sys
from tqdm import tqdm # for status bar

from image_tile_class import ImageClass


# IMPORT A PIPELINE SCRIPT WITH A NON-HARDCODED NAME (from any directory):
pipeline_path2_temp = sys.argv[2]
# parse powershell / command line input to strinig use:
pipeline_path2 = pipeline_path2_temp.replace("\\", "/")
# build new path, without the /pipeline:
pipeline_name_temp_list = pipeline_path2.split("/")
pipeline_name = pipeline_name_temp_list[-1]
if pipeline_name[-3:] == ".py":
	pipeline_name = pipeline_name[:-3]
pipeline_path2_dir = pipeline_name_temp_list[:-1]
pipeline_path2_dir = "/".join(pipeline_path2_dir)
pipeline_path2_dir = pipeline_path2_dir.replace("+", " ")
pipeline_path2_dir = pipeline_path2_dir + "/"
# add path (to the pipeline script) to the sys-path.  
sys.path.append(pipeline_path2_dir)
# import the whatever-called pipeline:
pipeline = __import__(pipeline_name)







class CallParallel():
	"""
	Contains all logic of the module.
	"""

	def __init__(self, csv_file_path, library_path, primary_staining, secondary_staining, tertiary_staining, no_debugging, get_full_image):
		"""
		Defines the pickle and library path.
		"""  
		self.csv_file_path = csv_file_path 
		self.library_path = library_path
		sys.path.append(library_path) # assumption: does not change it's location again
		self.image_object_module = __import__("ImageObject")
		self.primary_staining = primary_staining
		self.secondary_staining = secondary_staining
		self.tertiary_staining = tertiary_staining
		self.no_debugging = int(no_debugging)
		if get_full_image == "True":
			self.get_full_image = True
		else:
			self.get_full_image = False

		self.staining_list = [self.primary_staining, self.secondary_staining]

	





	def create_image_class_sub_list(self):
		self.image_class_sub_list = []
		f = open(self.csv_file_path)
		for line in f:
			temp_list = line.split(", ")
			temp_list = temp_list[:-1] # remove \n

			x_coord		= int(temp_list[3])
			y_coord		= int(temp_list[4])
			tile_size 	= int(temp_list[5])
			x_black_pixel	= int(temp_list[6])
			y_black_pixel	= int(temp_list[7])
			image_name 		= temp_list[0]
			import_path		= temp_list[1]
			save_path		= temp_list[2]
			layer			= int(temp_list[8])
			x_tile_count 	= int(temp_list[9])
			y_tile_count 	= int(temp_list[10])
			tile_id			= str(layer) + "_" + str(y_tile_count) + "_" + str(x_tile_count)
			coordinates_tuple	= (x_coord, y_coord, tile_size, x_black_pixel, y_black_pixel)
			image_object 		= ImageClass(image_name, import_path, save_path, coordinates_tuple, layer, tile_id, self.get_full_image)
			
			self.image_class_sub_list.append(image_object)
			self.arguments = {}		
			self.arguments["nuclei"] = (save_path + "nuclei"+os.sep)
			self.arguments["cellobjects"] = (save_path + "cellobjects"+os.sep)
			self.arguments["tmp"] = (save_path + "tmp"+os.sep)
			self.arguments["results"] = (save_path + "results"+os.sep)

	
	def clear_csv_files(self):
		"""
		removes corresponding csv file and the csv directory if empty
		"""
		os.remove(self.csv_file_path)
		temp = self.csv_file_path.split("/")
		temp = temp[:-1]
		csv_dir = "/".join(temp) + "/"
		if not os.listdir(csv_dir):
			os.rmdir(csv_dir)


	def initiate_pipeline(self, image_object): # !! note that all code will be excecuted within the jvm !! 
		"""
		Numpy array for image tile object is calculated. 
		Image tile object (image_tile_class.py -> ImageClass class object) is transferred to a new image object (image_class.py -> ImageObject class object).
		New Image object is restricted in the information and methods availible for the pipeline.
		Pipeline script is called for the current (new) image tile object.
		"""
		image_object.calc_RGB_numpy_array()
		clean_image_object = getattr(self.image_object_module, "ImageObject")
		uint8_array = image_object.get_RGB_numpy_array().astype(np.uint8)
		
		tile_object = clean_image_object(image_object.get_id(), image_object.get_name(), uint8_array, image_object.get_x(), image_object.get_y(), image_object.get_tile_width(), image_object.get_tile_height(), image_object.get_layer(), self.staining_list)

		# has to be discussed wether this stayes in the svs_reader on the long term
		save_path = image_object.save_path
		del image_object

		# excecuting the user defined pipeline:
		pipeline.main(tile_object, self.arguments, library_path)
		del tile_object


	def image_pipeline(self):
		"""
		Iterates through the list of image tile objects. Calls the initiate_pipeline method.
		For each tile all steps defined in the pipeline script will be applied to that tile.
		"""

		# starting one JVM that handels the iterative code - ugly but apparently no way around this
		print("-- starting CallParallel JVM --")
		jv.start_vm(class_path=bf.JARS, max_heap_size="6G")
		# the following 5 lines get rid of a really excited javabridge debugging output, as it is eager to tell you everything it is currently doing. javabridge always has a bright day and a lot to talk about.
		if self.no_debugging == 1:
			myloglevel="ERROR"
			rootLoggerName = jv.get_static_field("org/slf4j/Logger","ROOT_LOGGER_NAME", "Ljava/lang/String;")
			rootLogger = jv.static_call("org/slf4j/LoggerFactory","getLogger", "(Ljava/lang/String;)Lorg/slf4j/Logger;", rootLoggerName)
			logLevel = jv.get_static_field("ch/qos/logback/classic/Level",myloglevel, "Lch/qos/logback/classic/Level;")
			jv.call(rootLogger, "setLevel", "(Lch/qos/logback/classic/Level;)V", logLevel)	

		# iterate through the list of image tile objects -> for each the pipeline script is executed
		for i in tqdm(range(len(self.image_class_sub_list))):
			self.initiate_pipeline(self.image_class_sub_list[i])	
			self.image_class_sub_list[i] = None

		print("-- killing CallParallel JVM --")
		jv.kill_vm() 
	 

##########################################################			

def parse_backslash(string):
	"""
	Parses a Windows command line input into a python compatible path.
	"""
	new_string = string.replace("\\", "/")
	return new_string


def main(csv_file_path, library_path, primary_staining, secondary_staining, tertiary_staining, no_debugging, get_full_image):
	"""
	Main logic of the Class. Image list gets unpickled 
	and processed via the pipeline as interface to the Imaging Library.
	"""
	print("-- starting pipeline --")
	call_parallel = CallParallel(csv_file_path, library_path, primary_staining, secondary_staining, tertiary_staining, no_debugging, get_full_image)
	call_parallel.create_image_class_sub_list()
	call_parallel.image_pipeline()
	print("-- done with pipeline --")


if __name__ == '__main__':
	csv_file_path = 			parse_backslash(sys.argv[1])
	csv_file_path = 			csv_file_path.replace("+", " ")
	library_path_temp = 	parse_backslash(sys.argv[3])	
	library_path = 			library_path_temp.replace("+", " ")
	library_path = 			parse_backslash(library_path)
	primary_staining = 		sys.argv[4]
	secondary_staining = 	sys.argv[5]
	tertiary_staining = 	sys.argv[6]
	no_debugging = 			sys.argv[7]
	get_full_image = 		sys.argv[8]


	main(csv_file_path, library_path, primary_staining, secondary_staining, tertiary_staining, no_debugging, get_full_image)


	


