"""
The SVSReader class contains and calls the main logic. All additional modules are called within thi class. 
It does not manage the interface to the Imaging Library, this is part of the CallParallel class. 
The CallParallel class is from a logical and structural point of view part of the SVSReaader Class. The inability
to start more than one JVM from a python script led to it being a seperate module. 
"""

import javabridge as jv
import bioformats as bf
import multiprocessing as mp
import pickle # used for passing a list with empty image_class objects -> I/O is negliable

import sys
import os
import subprocess
#import wmi # for fetching running processes in win 
# make sure to install pypiwin32 as well

import timeit # to determine runtime
from tqdm import tqdm # for fancy status bar

import networkx
import importlib.util
import inspect
from pathlib import Path
from functools import partial
from copy import deepcopy



from svs_reader_lib.tile_provider import TileProvider
from svs_reader_lib.image_tile_class import ImageClass
from svs_reader_lib.image_reader_config import ImageReaderConfig
from svs_reader_lib.image_metadata import ImageMetadata
from svs_reader_lib.provide_ROI import ROI 
import svs_reader_lib.parse_command_line_input as parser
import PostprocessingThread

from scipy import misc

class SVSReader():
	"""
	Main logic of the SVS-Reader. Everything except cammand line parsing of the paths is handled within this class.
	"""
	def __init__(self, layer, get_full_image, post_processing_active, region_of_interrest_active, import_path, output_path, pipeline_path, post_pipe_path, impro_path, primary_staining, secondary_staining, tertiary_staining, no_debugging):
		"""
		Initilizes all mandatory variables. 
		Logic of the TileProvider is excecuted here.
		List containing all (empty -> no numpy arrays) image tile objects is created here.
		"""	
		
		# fetch all paths:
		self.layer = 				layer
		self.get_full_image = 		get_full_image
		self.pp_active = 			post_processing_active
		self.roi_active = 			region_of_interrest_active
		if no_debugging:
			self.no_debugging = 	1
		else:
			self.no_debugging = 	0
		self.impro_path = 			impro_path
		self.library_path = 		self.impro_path + "/imaging_lib" # + instead of space
		self.import_path = 			import_path
		self.pipeline_path = 		pipeline_path
		self.post_pipe_path = 		post_pipe_path
		self.output_path = 			output_path
		if self.output_path == 		None:
			self.output_path = 		impro_path + "/workspace3000/"
		self.check_for_and_create_dir(self.output_path)


		# fetch all info from the config:
		self.config = 		ImageReaderConfig()
		self.cores = 		self.config.cores
		#self.import_graph = self.config.import_graph
		#self.import_mapping = self.config.import_mapping


		self.__prepare_workspace()

		self.csv_dump_folder = 		"__csv_dump/"
		self.initiate_additional_paths()
		

		self.primary_staining = 		primary_staining
		if self.primary_staining == 	None:
			self.primary_staining = 	"unknown"
		self.secondary_staining	= 		secondary_staining
		if self.secondary_staining == 	None:
			self.secondary_staining = 	"unknown"
		self.tertiary_staining	= 		tertiary_staining
		if self.tertiary_staining == 	None:
			self.tertiary_staining = 	"unknown"

		# fetch all metadata:
		metadata = 	ImageMetadata(self.import_path, self.layer)

		# ROI
		layer3_roi = None
		if self.roi_active:
			roi = ROI(self.import_path, self.library_path, self.arguments["tmp"])
			layer3_roi = roi.return_layer3_RGB()
			misc.imsave(self.arguments["tmp"]+"ROI.tif",layer3_roi)

		# TILE PROVIDER ACTIONS:
		tile_provider = TileProvider(self.layer, self.get_full_image, self.roi_active, layer3_roi, metadata, self.config.tile_size, self.config.overlap)
		tile_provider.calc_coordinates()
		# list of coordinates:
		tile_provider.set_coordinates_list_status()

		# init image tile lists:
		self.image_class_list = []	

		# CREATE LIST WITH IMAGE (TILE) OBJECTS:
		for i in tqdm(range(tile_provider.get_coordinates_list_length())):
			coord_tupel = 	tile_provider.get_next_tile() # (x_coord, y_coord, tile_size, x_black_pixel, y_black_pixel)
			current_x = 	coord_tupel[0]
			current_y = 	coord_tupel[1]
			x_black = 		coord_tupel[3]
			y_black = 		coord_tupel[4]
			x_tile_count = 	coord_tupel[5]
			y_tile_count = 	coord_tupel[6]
			image_string = 	self.get_img_name() + ", " + str(self.import_path) + ", " + str(self.output_path) + ", "  + str(current_x) + ", " + str(current_y) + ", " + str(self.config.tile_size) + ", " + str(x_black) + ", " + str(y_black) + ", " + str(self.layer) + ", " + str(x_tile_count) + ", " + str(y_tile_count) + ", "
			self.image_class_list.append(image_string)





	def get_img_name(self):
		"""
		parse image name ot of the import path.
		"""
		file = Path(self.import_path)
		return file.stem

	def initiate_additional_paths(self):
		"""
		making additional paths available.
		"""
		self.csv_dir = self.impro_path + "/workspace3000/" + self.csv_dump_folder



	def __prepare_workspace(self):
		"""
		creating working directory
		"""
		self.arguments = {}
		folder = Path(self.import_path)
		self.output_path = self.__observe_path_for_existence(self.output_path + folder.stem + os.sep)		
		self.arguments["nuclei"] 		= self.__observe_path_for_existence(self.output_path + "nuclei"+os.sep)
		self.arguments["cellobjects"] 	= self.__observe_path_for_existence(self.output_path + "cellobjects"+os.sep)
		self.arguments["tmp"] 			= self.__observe_path_for_existence(self.output_path + "tmp"+os.sep)
		self.arguments["results"] 		= self.__observe_path_for_existence(self.output_path + "results"+os.sep)
		self.arguments["input_path"] 	= self.import_path
		"""
		self.arguments["input_graph"] 	= self.import_graph
		self.arguments["input_mapping"] = self.import_mapping
		self.arguments["img_name"]		= self.get_img_name()
		self.arguments["impro_path"] 	= self.impro_path
		"""


	def divide_image_class_list(self):
		"""
		Devide the list of image tile objects into sublists. Core count sublists are created.
		"""
		sub_length_temp = len(self.image_class_list) / self.cores
		sub_length = int(sub_length_temp)	# if len(image_class_list) / cores != int  a cores+1th list is added. runtime performance negligable, at most cores-1 elements in there 
		self.image_class_sub_lists = [self.image_class_list[x:x+sub_length] for x in range(0, len(self.image_class_list), sub_length)]


	def set_image_class_sublist(self):
		"""
		Check if the list of image tile objects has more items than core count. If not, set core count to one,
		as processing will be faster on one core than calling pool map.
		Call divide_image_class_list either way to obtain the correct list structure. 
		"""
		if len(self.image_class_list) >= self.cores:
			self.divide_image_class_list()
		else:
			self.cores = 1
			self.divide_image_class_list()



	def check_for_and_create_dir(self, path):
		if not os.path.exists(path):
			os.mkdir(path)
		
	def __observe_path_for_existence(self, path):
		file = Path(path)
		if not file.is_dir():
			os.makedirs(path)
		return path




	def write_csv_list(self, image_sublist, counter):
		"""
		Pickles each sublist of the image tile objedcts.
		Is called in run_call_parallel_once.
		"""
		self.csv_file_path = self.csv_dir + "tile_sublist_no_" + str(counter) + ".csv"
		f = open(self.csv_file_path,"w")
		for image_string in image_sublist:
			f.write(image_string+"\n")
		f.close()
	

	def space_to_plus(self, string):
		"""
		Replaces all spaces in a string with plus (+) symbol. 
		Used to work with paths that contain spaces.
		"""
		new_string = string.replace(" ", "+")
		return new_string


	def run_call_parallel_once(self,image_sublist):
		"""
		Calls the CallParallel module with all neccessary parameters. 
		CallParallel will run as an independant python script.
		"""
		counter = self.image_class_sub_lists.index(image_sublist)
		self.check_for_and_create_dir(self.csv_dir)
		self.write_csv_list(image_sublist, counter)
		self.call_parallel_path = self.impro_path.replace("+", " ") + "/reader/svs_reader_lib/call_parallel.py"
		self.call_parallel_path = '"' + self.call_parallel_path + '"'
		os.system("python " + self.call_parallel_path + " " + self.space_to_plus(self.csv_file_path) + " " + self.space_to_plus(self.pipeline_path) + " " + self.library_path + " " + self.primary_staining + " " + self.secondary_staining + " " + self.tertiary_staining + " " + str(self.no_debugging) + " " + str(self.get_full_image))  
		self.path_to_delete = self.csv_file_path


	def run_call_parallel(self):
		"""
		Executes run_call_parallel_once on each of core count cores.
		"""
		sublists = []
		for sublist in self.image_class_sub_lists:
			sublists.append(sublist)
		if self.pp_active:
			threads = self.__start_threads(self.get_identifier(self.import_path),self.arguments)
		p = mp.Pool(processes=self.cores)
		pooled_function = partial(self.run_call_parallel_once)
		p.map(pooled_function, sublists)
		self.clear_csv_files()
		return self.__close_threads(threads)

	


	def clear_csv_files(self):
		"""
		removes corresponding csv file and the csv directory if empty
		"""
		if os.listdir(self.csv_dir) and self.csv_dump_folder in self.csv_dir:
			try:
				file_list = os.listdir(self.csv_dir)
				for item in file_list:
					os.remove(self.csv_dir + item)
				os.rmdir(self.csv_dir)
			except OSError:
				print("-- could not delete files. Win permission error. --")
	def get_layer(self):
		return self.layer






	############### POSTPROCESSING ###################

	def get_identifier(self, path):
		return os.path.dirname(path).split(os.sep)[-1]


	def identify_main(self, path):
		spec = importlib.util.spec_from_file_location("pipeline", path)
		pipeline = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(pipeline)
		functionList = inspect.getmembers(pipeline,inspect.isfunction)
		for function in functionList:
			if function[0] == "main":
				return function[1]

	
	def initiate_threadding(self):
		# starting postprocessing threads
		if self.pp_active:
			print("-- threadding for postprocessing initialized --")
			self.__start_threads()
		else:
			print("-- postprocessing is disabled, no threads are started --")


	def __start_threads(self,id, arguments):
		threads = {}
		nuclei_thread = PostprocessingThread.PostprocessingThread(self.get_img_name(),arguments["nuclei"])
		nuclei_thread.start()
		threads["nuclei_thread"] = nuclei_thread
		cellobject_thread = PostprocessingThread.PostprocessingThread(self.get_img_name(),self.arguments["cellobjects"])
		cellobject_thread.start()
		threads["cellobject_thread"] = cellobject_thread
		return threads
		

	def __close_threads(self,threads):
		cellgraphs = {}
		print("-- building cellgraph --")
		for key, thread in threads.items():
			cellgraphs[key] = thread.exit_and_get_cellgraph()
		return cellgraphs		
		
				
	def execute_postprocessing(self, nuclei_graph, cellobject_graph):
		print("-- starting postprocessing --")
		sys.path.append(self.impro_path)
		import graph_lib.CellGraph as cellgraphObject
		import PostprocessingThread
		main = self.identify_main(self.post_pipe_path)
		main(nuclei_graph, cellobject_graph, self.impro_path, self.import_path, self.arguments)
		print("-- finished postprocessing --")
		
		

		









def parse_backslash(string):
	"""
	Parses a Windows command line input into a python path notation.
	"""
	new_string = string.replace("\\", "/")
	return new_string


def parse_input_path(input_string):
	print(input_string)
	svs_images_list = []
	if input_string.split(".")[-1] == "svs":
		svs_images_list.append(input_string)
	else:
		if os.path.exists(input_string):
			image_list = os.listdir(input_string)
			for item in image_list:
				svs_images_list.append(input_string + item)
		else:
			print("else")
			svs_images_list = None
	return svs_images_list



def main(layer, get_full_image, post_processing_active, region_of_interrest_active, import_path, output_path, pipeline_path, post_pipe_path, impro_path, primary_staining, secondary_staining, tertiary_staining, no_debugging):
	"""
	Main method for the SVS-Reader. If layer is not specified via comamnd line, layer 0 is read. 
	"""	
	if layer == None:
		layer = 0
	svs_reader_parallel = SVSReader(layer, get_full_image, post_processing_active, region_of_interrest_active, import_path, output_path, pipeline_path, post_pipe_path, impro_path, primary_staining, secondary_staining, tertiary_staining, no_debugging)
	svs_reader_parallel.set_image_class_sublist()
	#svs_reader_parallel.initiate_threadding()
	cellgraphs = svs_reader_parallel.run_call_parallel()
	print("-- obtained cellgraps --")
	#svs_reader_parallel.clear_csv_files()

	if post_processing_active:
		print("-- entering postprocessing --")
		svs_reader_parallel.execute_postprocessing(cellgraphs["nuclei_thread"],cellgraphs["cellobject_thread"])
	print("-- parsed layer: ", svs_reader_parallel.get_layer(), " --")




if __name__ == '__main__':
	
	start_time = timeit.default_timer()

# FETCH COMMAND LINE INPUTS
	args = parser.parse_command_line()
	# layer:
	layer = args.layer
	# import path:
	import_path = args.import_path
	import_path = parse_backslash(import_path)
	# save path:
	output_path = args.output_path
	if output_path != None:
		output_path = parse_backslash(output_path)
		if output_path[-1:] != "/":
			output_path += "/"

	# Boolean defaults:
	get_full_image = args.get_full_image
	post_processing_active = args.post_processing_active
	region_of_interrest_active = args.region_of_interrest_active
	no_debugging = args.no_debugging
	# pipeline path
	pipeline_path_temp = args.pipeline_path
	pipeline_path = parse_backslash(pipeline_path_temp)
	pipeline_path = pipeline_path.replace(" ", "+")
	# postprocessing pipeline
	post_pipe_path_temp = args.postprocessing_pipeline_path
	post_pipe_path = parse_backslash(post_pipe_path_temp)


	# impro path:
	impro_path_temp = args.impro_path
	impro_path = parse_backslash(impro_path_temp)
	impro_path = impro_path.replace(" ", "+")
	# straining, can be None type
	primary_staining = args.primary_staining
	secondary_staining = args.secondary_staining
	tertiary_staining = args.tertiary_staining


# CALL MAIN

	print("-- starting SVSReader JVM --")
	jv.start_vm(class_path=bf.JARS, max_heap_size="250G")
	# the following 5 lines get rid of a really excited javabridge debugging output, as it is eager to tell you everything it is currently doing. javabridge always has a bright day and a lot to talk about.
	if no_debugging == 1:
		myloglevel = 		"ERROR"
		rootLoggerName = 	jv.get_static_field("org/slf4j/Logger","ROOT_LOGGER_NAME", "Ljava/lang/String;")
		rootLogger = 		jv.static_call("org/slf4j/LoggerFactory","getLogger", "(Ljava/lang/String;)Lorg/slf4j/Logger;", rootLoggerName)
		logLevel = 			jv.get_static_field("ch/qos/logback/classic/Level",myloglevel, "Lch/qos/logback/classic/Level;")
		jv.call(rootLogger, "setLevel", "(Lch/qos/logback/classic/Level;)V", logLevel)

	svs_path_list = parse_input_path(import_path)
	print(svs_path_list)
	for single_import_path in svs_path_list:
		print("\n##### ##### ##### ########## ##### ##### ##### \n")
		print(" SVS IMAGE: ", single_import_path.split("/")[-1])
		main(layer, get_full_image, post_processing_active, region_of_interrest_active, single_import_path, output_path, pipeline_path, post_pipe_path, impro_path, primary_staining, secondary_staining, tertiary_staining, no_debugging)	

	print("-- killing SVSReader JVM --")
	jv.kill_vm() 

	stop_time = timeit.default_timer()
	print("-- it took forever: ", stop_time - start_time, " seconds --")


