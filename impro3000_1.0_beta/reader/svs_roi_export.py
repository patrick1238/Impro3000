
import numpy as np
import bioformats as bf
import javabridge as jv



def get_subimage_as_numpy(path, layer, x_coord, y_coord, width, height):

	jv.start_vm(class_path=bf.JARS, max_heap_size="250G")

	image_reader = bf.ImageReader(path=path, perform_init=True) 
	data_read = image_reader.read(series=layer, XYWH=(x_coord, y_coord, width, height))
	
	image_reader.close()
	
	data_read = data_read * 255
	data_read = data_read.astype(int)
	rgb_numpy_array = data_read

	jv.kill_vm()
	
	return rgb_numpy_array



#def main(path, layer, x_coord, y_coord, width, height):
#	get_subimage_as_numpy(path, layer, x_coord, y_coord, width, height)

# TESTING:
def main():
	import scipy.misc
	path = "C:/Users/D.Va/Documents/Images_hendrik/8064-01III2_CD30.svs"
	layer = 0 
	numpy = get_subimage_as_numpy(path, layer, 8000, 8000, 5000, 5000)
	scipy.misc.imsave("C:/Users/D.Va/Desktop/test_svs_roi_export.tiff", numpy)


if __name__ == '__main__':
	main()




