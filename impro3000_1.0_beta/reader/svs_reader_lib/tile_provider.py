"""
The tile_provider modules calculates the grid and thereby the ccordinates for the single tiles that will be read from an svs image.
Taken into account are tilesize (length and width) and overlap.
Tiles at edges will be cut and therefore will not be squares. No data is added to fill in "missing" image data.
"""
from copy import deepcopy
class TileProvider():
	"""
	Contains all the main logic of the module
	""" 
	
	def __init__(self, layer, get_full_image, roi_active, layer3_roi, metadata, tile_size, overlap):
		"""
		Fetching all relevant information, like tilesize, overlap and metadata.
		"""
		self.get_full_image = 	get_full_image
		self.layer3_roi = 		layer3_roi
		self.roi_active = 		roi_active
		self.layer = 			layer
		self.tile_coordinates_list = []
		self.tile_coordinates_list_backup = []
		
		self.overlap = 			overlap
		self.tile_size = 		tile_size
		# collecting metadata
		self.metadata = 		metadata
		self.metadata.print_all_metadata()


		self.size_x = self.metadata.size_x
		self.size_y = self.metadata.size_y

		# scaling factors
		if self.layer == 0: # from layer 3 to 0
			self.resize = 32
		elif self.layer == 1: # from layer 3 to 1
			self.resize = 16
		elif self.layer == 2: # from layer 3 to 2
			self.resize = 4

	def calc_coordinates(self):
		"""
		Core functionality of the module, calcultes the grid over an image. For further details look into the code.
		Output is a list of coordinates with tuples (x_coord, y_coord, tile_size, x_black_pixel, y_black_pixel), 
		where the black pixels represent the overhang over the lower and / or right edge. The list can be accessed via the TileProvider class, 
		there is no return statement. 
		"""
		overlap = self.overlap
		tile_size = self.tile_size
		size_x = self.size_x
		size_y = self.size_y
		
		if self.get_full_image:
			temp_tuple = (0, 0, None, self.size_x, self.size_y, 0, 0)
			self.tile_coordinates_list.append(temp_tuple)
		else:

			# first calculate number of tiles needed:
			# in x direction
			number_of_x_tiles = size_x // (tile_size - overlap) # first calculate with "smaller" tiles to handle overlap, ignore last tile that has no overlap
			temp_x_mod = size_x % (tile_size - overlap)
			# Assumption: if (total x) mod ((tile size) - (overlap)) = overlap -> no tile has to be added, no pixel have to be added, the overlap is missing in the last tile
			# if the mod is smaller than the overlap, no additional tiles are needed, we end up with black / missing pixels
			if temp_x_mod > overlap: # if the mod is bigger than the overlap, we need an additional tile, this contains black / missing pixel
				number_of_x_tiles += 1			 
			# in y direction
			number_of_y_tiles = size_y // (tile_size - overlap) 
			temp_y_mod = size_y % (tile_size - overlap)
			if temp_y_mod > overlap:
				number_of_y_tiles += 1

			# add coordinate tupels to tile_coordinates_list -> tupel: (x_coord, y_coord, tile_size, x_black_pixel, y_black_pixel, x_tile_count, y_tile_count)
			print("\n##### ### TILE PROVIDER INFORMATION #### ##### \n")
			print("Tile size:\t", self.tile_size)
			print("Overlap:\t", self.overlap)
			print("Count of tiles in x direction: ", number_of_x_tiles)
			print("Count of tiles in y direction: ", number_of_y_tiles)

			y_tile_count = -1
			x_tile_count = -1

			# CALCULATING NEXT COORDINATES TUPLE:
			for y_tile in range(0, number_of_y_tiles):
				y_tile_count += 1
				for x_tile in range(0, number_of_x_tiles):
					x_tile_count += 1
					# tile is NOT at the lower edge, tile is NOT at the right edge:
					if x_tile < (number_of_x_tiles-1) and y_tile < (number_of_y_tiles-1):
						temp_tuple = (x_tile * (tile_size - overlap), (y_tile * (tile_size - overlap)), tile_size, 0, 0, x_tile_count, y_tile_count)				
					# tile is NOT at the lower edge, tile IS at the right edge:
					elif x_tile == (number_of_x_tiles-1) and y_tile < (number_of_y_tiles-1):
						temp_tuple = (x_tile * (tile_size - overlap), (y_tile * (tile_size - overlap)), tile_size, size_x - (x_tile * (tile_size - overlap)), 0, x_tile_count, y_tile_count)			
					# tile IS at the lower edge, tile is NOT at the right edge:
					elif x_tile < (number_of_x_tiles-1) and y_tile == (number_of_y_tiles-1):
						temp_tuple = (x_tile * (tile_size - overlap), (y_tile * (tile_size - overlap)), tile_size, 0, size_y - (y_tile * (tile_size - overlap)), x_tile_count, y_tile_count)
					# tile IS at the lower edge, tile IS at the right edge:
					elif x_tile == (number_of_x_tiles-1) and y_tile == (number_of_y_tiles-1):
						temp_tuple = (x_tile * (tile_size - overlap), (y_tile * (tile_size - overlap)), tile_size, size_x - (x_tile * (tile_size - overlap)), size_y - (y_tile * (tile_size - overlap)), x_tile_count, y_tile_count)
					# something went horribly wrong (no test case ever showed this):
					else:
						print("!!! [calculating tile] CASE NOT COVERED !!!")
					
					# Apply Region of Interrest Information:
					if not self.roi_active or self.layer >= 3:
						self.tile_coordinates_list.append(temp_tuple)
					else:
						# translate dimensions to layer3 
						roi_x_coord = int(temp_tuple[0] / self.resize)
						roi_y_coord = int(temp_tuple[1] / self.resize)
						roi_tile_size = int(temp_tuple[2] / self.resize)
						roi_x_black = int(temp_tuple[3] / self.resize) # last two won't be ints most likely, but reading 12.6 pixel is not possible. reading 12 is.
						roi_y_black = int(temp_tuple[4] / self.resize)

						l3_len_y = len(self.layer3_roi)
						l3_len_x = len(self.layer3_roi[0])


						interest_count = 0 
						for y in range(roi_y_coord, (roi_y_coord + roi_tile_size - roi_y_black)): # (roi_y_coord + roi_tile_size - roi_y_black)
							for x in range(roi_x_coord, (roi_x_coord + roi_tile_size - roi_x_black)):
								# check that we do not cross the border of l_3
								if (roi_y_coord + roi_tile_size - roi_y_black) <= l3_len_y and (roi_x_coord + roi_tile_size - roi_x_black) <= l3_len_x:
									if self.layer3_roi[y][x] > 0: # R
										interest_count += 1
						if interest_count > 1:			
							self.tile_coordinates_list.append(temp_tuple)
										
		

		self.tile_coordinates_list_backup = deepcopy(self.tile_coordinates_list) # maybe the whole is list is needed at some other point later? get_next_tile destroys the non backup list


		print("Total count of tiles: ", len(self.tile_coordinates_list))
		print("\n##### ##### ##### ########## ##### ##### ##### \n")

		print("-- done with calculating coordinates --")
	


	def get_next_tile(self):
		"""
		Returns the next tuple in the coordinates list. 
		Deletes the tuple from the coordinates list.

		:return: (tuple) (x_coord, y_coord, tile_size, x_black_pixel, y_black_pixel) 
		"""
		if len(self.tile_coordinates_list) > 1:
			next_tile = self.tile_coordinates_list[0]
			del self.tile_coordinates_list[0] 
			return next_tile
		else:
			next_tile = self.tile_coordinates_list[0]
			del self.tile_coordinates_list[0]
			self.set_coordinates_list_status()
			return next_tile


	def set_coordinates_list_status(self):
		"""
		Auxiliary method to determine wether the coordinates list is empty.
		"""
		if len(self.tile_coordinates_list) > 0:
			self.tile_coordinates_list_has_element = True
		else:
			self.tile_coordinates_list_has_element = False



	def get_coordinates_list_length(self):
		"""
		Returns length of coordinates list

		:return: (int) length of coordinates list
		"""
		return len(self.tile_coordinates_list_backup)





