# get metadata
import bioformats as bf
import javabridge as jv

import os

class ImageMetadata:
	def __init__(self, path_to_file, layer):
		self.layer = layer
		self.path_to_file = path_to_file
		
		self.meta_data = bf.get_omexml_metadata(path_to_file)

		print(self.meta_data)



		self.ome = 				bf.OMEXML(self.meta_data)
		self.image_count = 		self.ome.image_count
		self.image_count_2 = 	self.ome.get_image_count()
		
#		self.iome = 			self.ome.image() 
		self.iome = 			self.ome.image(self.layer) 

		#self.image_caps = 		self.ome.Image()
		#self.caps_id 	= 		self.image_caps.get_ID()

		self.instrument = 		self.ome.instrument()
		self.instrument_id = 	self.instrument.get_ID()
		#self.detector_id = 		self.instrument.Detector.get_ID()

		self.iome_names = 		self.iome.get_Name()
		self.iome_id = 			self.iome.get_ID()
		self.date_acq = 		self.iome.get_AcquisitionDate()

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
		print("Image Count:\t\t", 			self.image_count, self.image_count_2)
		print("Image Name:\t\t", 				self.iome_names)
		print("Image ID:\t\t", 				self.iome_id)
		print("Image Dimension Order:\t", 	self.dimension_order)
		print("Image Pixel Type:\t",		self.pixel_type)
		print("Acq Date:\t",		self.date_acq)
		#print("caps image id:\t",		self.caps_id)
		print("instrument id:\t",		self.instrument_id)#, self.detector_id)
		print("\nImage Values:\n")
		print("X:\t", 		self.size_x)
		print("Y:\t", 		self.size_y)
		print("Z:\t",		self.size_z)
		print("C:\t",		self.size_c)
		print("T:\t",		self.size_t)




def main():
	image_path_list = []
	dir_path = "C:/Users/D.Va/Documents/Images_hendrik/"
	image_list = os.listdir(dir_path)
	for item in image_list:
		image_path_list.append(dir_path + item)

	for current_path in image_path_list:
		image_metadata = ImageMetadata(current_path, 0)
		image_metadata.print_all_metadata()



if __name__ == '__main__':
	jv.start_vm(class_path=bf.JARS, max_heap_size="250G")
	# the following 5 lines get rid of a really excited javabridge debugging output, as it is eager to tell you everything it is currently doing. javabridge always has a bright day and a lot to talk about.

	myloglevel = 		"ERROR"
	rootLoggerName = 	jv.get_static_field("org/slf4j/Logger","ROOT_LOGGER_NAME", "Ljava/lang/String;")
	rootLogger = 		jv.static_call("org/slf4j/LoggerFactory","getLogger", "(Ljava/lang/String;)Lorg/slf4j/Logger;", rootLoggerName)
	logLevel = 			jv.get_static_field("ch/qos/logback/classic/Level",myloglevel, "Lch/qos/logback/classic/Level;")
	jv.call(rootLogger, "setLevel", "(Lch/qos/logback/classic/Level;)V", logLevel)

	main()

	jv.kill_vm() 
	print("--done--")






