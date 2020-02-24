import sys
sys.path.append("..")
from scipy import misc
import imaging_lib.CV_Celldetect as celldetect

def main(image_object, arguments, library_path):

    library_path = library_path
    sys.path.append(library_path)
    '''
    import general_properties
    generalprops = general_properties.measure_general_properties(image_object,arguments)
    outstring = "\nID: " + image_object.get_id() + "\n"
    for key in generalprops:
        outstring = outstring + key + ": " + str(generalprops[key]) + "\n"
    print(outstring)
    '''
    color_deconvolution = __import__("color_deconvolution")
    cd30_image_object, hematoxilin_image_object = color_deconvolution.colour_deconvolution(image_object)
    #celldetect.Detect_cells(cd30_image_object,arguments)
    #misc.imsave(arguments["tmp"]+cd30_image_object.get_id()+"_hematox.tif",hematoxilin_image_object.get_numpy_array())
    #print("-- importing module --")
    #from CellDetector import CellDetector 
    #cell_detector = CellDetector(arguments)
    #cell_detector.segment_tile(cd30_image_object, hematoxilin_image_object)    