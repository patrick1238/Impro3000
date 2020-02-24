# Image class -> gets imput like ccordiantes from imgae_reader, more precisely imgae_handler

import os
import sys

import timeit # for runtime
from tqdm import tqdm # for status bar

import numpy as np
import bioformats as bf


class ImageClass():
# aim: output image in numpy array
	def fromCSV():
		pass


	def toCSV():
		asCSV = self.import_path + "," + ""

		return asCSV

	def __init__(self, image_name, import_path, save_path, get_next_tile, layer, tile_id, get_full_image):
		self.image_name = image_name
		self.import_path = import_path
		self.save_path = save_path
		self.current_tile_information = get_next_tile # tupel obtained from TileProvider.get_next_tile()
		self.layer = layer
		info = self.current_tile_information
		self.x_coord = info[0]
		self.y_coord = info[1]
		self.tile_size = info[2]
		self.tile_id = tile_id
		self.get_full_image = get_full_image
		# x direction:
		if self.current_tile_information[3] == 0:
			self.width = self.current_tile_information[2]
		else:
			self.width = self.current_tile_information[3] #3
		# y direction:
		if self.current_tile_information[4] == 0:
			self.height = self.current_tile_information[2]
		else:
			self.height = self.current_tile_information[4] #4





	
	def calc_RGB_numpy_array(self):
		info = self.current_tile_information
		image_reader_2 = bf.ImageReader(path=self.import_path, perform_init=True) 
		# calc_coordinates tupel: (x_coord, y_coord, tile_size, x_black_pixel, y_black_pixel)
		# read tupel = (x,y, w,h)
		data_read = image_reader_2.read(series=self.layer, XYWH=(self.x_coord, self.y_coord, self.width, self.height))
		
		image_reader_2.close()
		
		data_read = data_read * 255
		data_read = data_read.astype(int)
		self.rgb_numpy_array = data_read
		if not self.get_full_image:
			self.make_to_square()



	def make_to_square(self):
		#for i in self.rgb_numpy_array:
		#	print(len(i))
		black_x = self.tile_size - self.width
		black_y = self.tile_size - self.height

		if black_y != 0 or black_x != 0:
			old_array = self.rgb_numpy_array
			new_array = np.ndarray((self.tile_size, self.tile_size, 3))

			new_array[:,:,0] = 0
			new_array[:,:,1] = 0
			new_array[:,:,2] = 0
			new_array = new_array.astype(int)

			new_array[0:self.height, 0:self.width] = self.rgb_numpy_array

			self.rgb_numpy_array = new_array
			self.width = self.tile_size
			self.height = self.tile_size



	def get_RGB_numpy_array(self):
		return self.rgb_numpy_array


	def write_tiff(self, numpy_array):
		pixels = numpy_array
		image_writer = bf.write_image(self.save_path, numpy_array, "uint8")


	def get_tile_width(self):
		return self.width


	def get_tile_height(self):
		return self.height


	def get_x(self):
		return self.x_coord


	def get_y(self):
		return self.y_coord

	def get_import_path(self):
		return self.import_path

	def get_layer(self):
		return self.layer

	def get_name(self):
		return self.image_name

	def get_id(self):
		return self.tile_id










