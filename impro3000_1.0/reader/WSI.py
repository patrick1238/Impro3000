# -*- coding: utf-8 -*-

import sys
sys.path.append("..")
import bioformats as bf
from pathlib import Path
import numpy as np
import std_pckgs.Diagnose_handler as diagnose_handler


class WSI():
	
	input_path = None
	ome = None
	image_name = None
	diagnose = None

	def __init__(self, input_path):
		self.input_path = input_path
		self.read_metadata()
		file = Path(self.input_path)
		index = file.stem.find('.')#+3
		self.image_name = file.stem#[0:index]
		Diagnose_handler = diagnose_handler.Diagnose_handler()
		self.diagnose = Diagnose_handler.get(self.image_name)


	def read_metadata(self):
		meta_data = bf.get_omexml_metadata(self.input_path)
		self.ome 	= bf.OMEXML(meta_data)

	
	def get_width(self, layer):
		iome = self.ome.image(layer)
		return iome.Pixels.get_SizeX()


	def get_height(self, layer):
		iome = self.ome.image(layer)
		return iome.Pixels.get_SizeY()


	def get_layer_count(self):
		return self.ome.image_count
	
	
	def get_image_name(self):
		return self.image_name
		
	def get_diagnose(self):
		return self.diagnose


	
	def get_RGB_numpy_array(self, x_coord=0, y_coord=0, width=-1, height=-1, layer=0):
		""" calculates the numpy array via bioformats. """
		if height == -1:
			height = self.get_height(layer)
		if width == -1:
			width = self.get_width(layer)
		image_reader = bf.ImageReader(path=self.input_path, perform_init=True) # what does the init do? no idea.
		tmp_nparray = image_reader.read(series=layer, XYWH=(x_coord, y_coord, width, height))
		image_reader.close()		
		tmp_nparray = tmp_nparray * 255
		rgb_numpy_array = tmp_nparray.astype(np.uint8)	
		return rgb_numpy_array


	






