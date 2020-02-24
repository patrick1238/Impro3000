# get metadata
import bioformats as bf

class ImageMetadata:
	def __init__(self, path_to_file, layer):
		self.layer = layer
		self.path_to_file = path_to_file
		
		self.meta_data = bf.get_omexml_metadata(path_to_file)

		self.ome = 				bf.OMEXML(self.meta_data)
		self.image_count = 		self.ome.image_count
		
#		self.iome = 			self.ome.image() 
		self.iome = 			self.ome.image(self.layer) 

		self.iome_names = 		self.iome.get_Name()
		self.iome_id = 			self.iome.get_ID()

		self.dimension_order = 	self.iome.Pixels.get_DimensionOrder()
		self.pixel_type = 		self.iome.Pixels.get_PixelType()
		self.size_x = 			self.iome.Pixels.get_SizeX()
		self.size_y = 			self.iome.Pixels.get_SizeY()
		self.size_z = 			self.iome.Pixels.get_SizeZ()
		self.size_t = 			self.iome.Pixels.get_SizeT()
		self.size_c = 			self.iome.Pixels.get_SizeC()


		self.pixels_names = 	bf.OMEXML(self.meta_data).image().Name
		self.acquisition_date = bf.OMEXML(self.meta_data).image().AcquisitionDate

		#jv.kill_vm()
	def print_all_metadata(self):
		print("\n#####  OUTPUT OF ALL ACCESSIBLE METADATA ##### \n")
		print("Image Count:\t\t", 			self.image_count)
		print("Image Name:\t\t", 				self.iome_names)
		print("Image ID:\t\t", 				self.iome_id)
		print("Image Dimension Order:\t", 	self.dimension_order)
		print("Image Pixel Type:\t",		self.pixel_type)
		print("\nImage Values:\n")
		print("X:\t", 		self.size_x)
		print("Y:\t", 		self.size_y)
		print("Z:\t",		self.size_z)
		print("C:\t",		self.size_c)
		print("T:\t",		self.size_t)




