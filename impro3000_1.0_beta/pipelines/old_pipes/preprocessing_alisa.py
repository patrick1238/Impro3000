import sys
import os
from random import randint
from scipy import misc
#sys.path.append("../imaging_lib/")
#from imaging_lib import color_deconvolution
#from imaging_lib import SegmenterNucleiUnet

def main(image_object, arguments, library_path):
    print("Preprocessing started")
    print("-- tile sizes in pipeline --")
    print("IMAGE OBJECT: \n\n", image_object.get_numpy_array())
    print("width:  ", image_object.get_width())
    print("height: ", image_object.get_height())
    library_path = library_path
    sys.path.append(library_path)
    color_deconvolution = __import__("color_deconvolution")
    cd30,hematoxilin = color_deconvolution.colour_deconvolution(image_object)
    misc.imsave(arguments["tmp"]+cd30.get_id()+"_cd30.tif",cd30.get_numpy_array())
    misc.imsave(arguments["tmp"]+"test2.tif",hematoxilin.get_numpy_array())
    save_as_tiff = __import__("save_as_tiff")
    save_as_tiff.main(hematoxilin, arguments["tmp"])
    SegmenterNucleiUnet = __import__("SegmenterNucleiUnet")
    nuclei_segmentation = SegmenterNucleiUnet.SegmenterNucleiUnet(hematoxilin,arguments["nuclei"])
    image = nuclei_segmentation.segment()
