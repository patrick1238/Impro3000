import sys
import numpy as np
import bioformats as bf

class ROI():

	def __init__(self, import_path, library_path, output_path):
		
		sys.path.append(library_path) # assumption: does not change it's location again
		self.roi_lib_module = __import__("region_of_interest")
		self.output_path = output_path 


		self.image_path = import_path

		self.layer = 3		
		self.meta_data = bf.get_omexml_metadata(import_path)

		self.ome = 				bf.OMEXML(self.meta_data)		
		self.iome = 			self.ome.image(self.layer) 
		self.size_x = 			self.iome.Pixels.get_SizeX()
		self.size_y = 			self.iome.Pixels.get_SizeY()


	def calc_layer3_RGB(self):
		print("-- obtaining layer 3 RGB numpy array --")
		#info = self.current_tile_information
		image_reader_2 = bf.ImageReader(path=self.image_path, perform_init=True) # no fucking clue what the init does
		# calc_coordinates tupel: (x_coord, y_coord, tile_size, x_black_pixel, y_black_pixel)
		# read tupel = (x,y, w,h)
		data_read = image_reader_2.read(series=self.layer, XYWH=(0, 0, self.size_x, self.size_y))
		
		image_reader_2.close()
		
		data_read = data_read * 255
		data_read = data_read.astype(int)

		return data_read

	def deploy_roi_lib_module(self, image, dimension, working_dir, roi_threshold):
		print("-- converting layer 3 image to binary --")
		#ROI_class = getattr(self.roi_lib_module, "region_of_interest")
		binary_layer_3 = self.roi_lib_module.calculateROI(image, dimension, working_dir, roi_threshold)
		return binary_layer_3


	def return_layer3_RGB(self):
		layer_3_image = self.calc_layer3_RGB()
		layer_3_binary = self.deploy_roi_lib_module(layer_3_image, 500, self.output_path, 200)
		#print(layer_3_binary)
		return layer_3_binary

