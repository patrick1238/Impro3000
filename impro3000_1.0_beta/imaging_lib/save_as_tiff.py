import scipy.misc

def save_as_tiff(image_object, path):
	numpy_array = image_object.get_numpy_array()
	scipy.misc.imsave(path+image_object.get_name()+"_"+image_object.get_id()+".tif", numpy_array)

