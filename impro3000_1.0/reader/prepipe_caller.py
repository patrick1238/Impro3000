# -*- coding: utf-8 -*-
import bioformats as bf
import javabridge as jv
import numpy as np
import sys
sys.path.append("..")
import WSI
from imaging import image
import argparse as ap
import os
from reader.std_pckgs.basic_functions import identify_main


no_debugging = True
parser_new = ap.ArgumentParser()
parser_new.add_argument("-dump", "--dump_path", help="enter path for csv_path", type=str, default=None)
parser_new.add_argument("-i", "--input_path", help="enter input_path to image file", type=str, default=None)
parser_new.add_argument("-o", "--output_path", help="enter path to the output folder", type=str, default=None)
parser_new.add_argument("-prepipe", "--prepipe", help="enter name of the prepipeline", type=str, default=None)
parser_new.add_argument("-staining", "--staining", help="given staining", type=str, default=None)
parser_new.add_argument("-ts", "--tile_size", help="tile size", type=str, default=None)
parser_new.add_argument("-l", "--layer", help="layer", type=str, default=None)
args = parser_new.parse_args()


def __parse_csv_to_sublist():
    image_class_sub_list = {}
    f = open(args.dump_path)
    for line in f:
        line = line.strip("\n").replace(" ","")
        temp_list     = line.split(",")
        tile_id = temp_list[0]
        x_coord        = int(temp_list[1])
        y_coord        = int(temp_list[2])
        width = int(temp_list[3])
        height = int(temp_list[4])
        image_class_sub_list[tile_id] = (x_coord,y_coord,width,height)
    return image_class_sub_list



def __clear_csv_files():
    """
    removes corresponding csv file and the csv directory if empty
    """
    os.remove(args.dump_path)
    temp = args.dump_path.split("/")
    temp = temp[:-1]
    csv_dir = "/".join(temp) + "/"
    if not os.listdir(csv_dir):
        os.rmdir(csv_dir)




def __check_for_square(rgb_numpy_array, width, height, tile_size):
    """ transform the tile_array into square (tilesize x tilesize), if neccessary. """

    # check if it is necessary to transform tile to square:
    if width < tile_size or height < tile_size:
        new_array = np.ndarray((tile_size, tile_size, 3))
        # fill array black:
        new_array[:,:,0] = 255
        new_array[:,:,1] = 255
        new_array[:,:,2] = 255
        new_array = new_array.astype(int)
        # replace black with original tile array, over-the-edge area remains black:
        new_array[0:height, 0:width] = rgb_numpy_array    
        # update tiles measurements:
        return new_array
    else:
        return rgb_numpy_array

def __start_jvm():
    jv.start_vm(class_path=bf.JARS, max_heap_size="12G")
    if no_debugging == True:
        myloglevel="ERROR"
        rootLoggerName = jv.get_static_field("org/slf4j/Logger","ROOT_LOGGER_NAME", "Ljava/lang/String;")
        rootLogger = jv.static_call("org/slf4j/LoggerFactory","getLogger", "(Ljava/lang/String;)Lorg/slf4j/Logger;", rootLoggerName)
        logLevel = jv.get_static_field("ch/qos/logback/classic/Level",myloglevel, "Lch/qos/logback/classic/Level;")
        jv.call(rootLogger, "setLevel", "(Lch/qos/logback/classic/Level;)V", logLevel)
    
def __execute_pipeline(image_class_sub_list):
    """ 
    dict arguments is created;
    rgb_numpy_array is calculated;
    'correct' image object is created;
    pipeline is called.
    """
    # create argmuments dict for pipeline:
    arguments = {}
    arguments["tmp"]         = args.output_path + "tmp/"
    arguments["cellobjects"] = args.output_path + "tmp/cellobjects_dump/"
    arguments["results"]     = args.output_path + "results/"
    arguments["input_path"]  = args.input_path

    # create one WSI object, used for all rgb_numpy_calculations:
    wsi_object = WSI.WSI(args.input_path)
    # iterate over the entire tile_sublist:
    for tile in image_class_sub_list:
        coordinates_tuple     = image_class_sub_list[tile]
        layer = int(args.layer)
        # calculate rgb_numpy_array on the WSI object for current tile:
        tmp_nparray = wsi_object.get_RGB_numpy_array(coordinates_tuple[0], coordinates_tuple[1], coordinates_tuple[2], coordinates_tuple[3], layer)
        # make to sqaure if neccessary:
        tile_size = int(args.tile_size)
        square_tmp_array = __check_for_square(tmp_nparray, coordinates_tuple[2], coordinates_tuple[3], tile_size)
        rgb_numpy_array = square_tmp_array.astype(np.uint8)
        
        # create 'correct' tile_object:
        tile_object = image.Image(tile, wsi_object.get_image_name(), rgb_numpy_array, coordinates_tuple[0], coordinates_tuple[1], tile_size, tile_size, layer, args.staining)

        # execute pipeline:
        prepipe_main = identify_main(args.prepipe)
        prepipe_main(tile_object, arguments)

# do all the stuff above:
__start_jvm()
image_class_sub_list=__parse_csv_to_sublist()
__clear_csv_files()
__execute_pipeline(image_class_sub_list)
jv.kill_vm()







    

