# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 10:15:36 2019

@author: patri
"""
import sys
sys.path.append("..")
from std_pckgs import Config
from WSI_reader_lib import Tile_provider
from imaging import roi_detector
from functools import partial
import javabridge as jv
import bioformats as bf
import Postprocessing_thread as post_thread
import multiprocessing as mp
import WSI
import os
from imaging import image
import time
from reader.std_pckgs.basic_functions import identify_main
from reader.std_pckgs.basic_functions import prepare_workspace

no_debugging = True
__SCRIPT_NAME = "[WSI Reader]"

def initialize_javabridge():
    jv.start_vm(class_path=bf.JARS, max_heap_size="12G")
    if no_debugging == True:
        myloglevel =         "ERROR"
        rootLoggerName =     jv.get_static_field("org/slf4j/Logger","ROOT_LOGGER_NAME", "Ljava/lang/String;")
        rootLogger =         jv.static_call("org/slf4j/LoggerFactory","getLogger", "(Ljava/lang/String;)Lorg/slf4j/Logger;", rootLoggerName)
        logLevel =           jv.get_static_field("ch/qos/logback/classic/Level",myloglevel, "Lch/qos/logback/classic/Level;")
        jv.call(rootLogger, "setLevel", "(Lch/qos/logback/classic/Level;)V", logLevel)   

def start_thread(image_name, diagnose, arguments):
    cellobject_thread = post_thread.Postprocessing_thread(image_name,diagnose,arguments["cellobjects"])
    cellobject_thread.start()
    return cellobject_thread
        
def analyse_graph(cellgraph,arguments,config):
    main = identify_main(config.get("postprocessing_pipeline"))
    main(cellgraph,arguments)
    
def evaluate_image(config):
    eval_pipe = identify_main(config.get("evaluation_pipeline"))
    eval_pipe(config)

def process_tile(path,arguments,prepipe,config):
    call = "python ./prepipe_caller.py -dump \"" +arguments["csv_dump"] + path + "\" -i \""+arguments["input_path"]+"\" -o \""+arguments["output_path"]+"\\\" -prepipe \"" + prepipe+"\" -staining \"" + config.get("staining") + "\" -ts \"" +config.get("tile_size")+"\" -l \"" +str(config.get("layer"))+"\""
    os.system(call)  

def analyse_image(image_file,config):
    wsi = WSI.WSI(image_file)
    layer = int(config.get("layer"))
    print(__SCRIPT_NAME+": Starting to analyse: " + wsi.get_image_name())
    arguments = prepare_workspace(wsi.get_image_name(),config.get("output_path"))
    arguments["input_path"] = image_file
    if config.get("postprocessing_active")=="active":
        cellobject_thread = start_thread(wsi.get_image_name(),wsi.get_diagnose(),arguments)
    if config.get("get_full_image") == True:
        prepipe = identify_main(config.get("preprocessing_pipeline"))
        print(wsi.get_width(0),wsi.get_height(0))
        image_object = image.Image(str(layer)+".0.0",wsi.get_image_name(),wsi.get_RGB_numpy_array(layer=layer),0,0,wsi.get_width(layer),wsi.get_height(layer),layer,config.get("staining"))
        prepipe(image_object,arguments)
    else:
        roi = roi_detector.detect_roi(wsi.get_RGB_numpy_array(layer=3))
        tile_provider = Tile_provider.TileProvider(wsi)
        resize = wsi.get_width(layer)/wsi.get_width(3)
        tile_provider.calc_image_tiles(layer=layer,roi=roi,resize=resize)
        cores = min(int(config.get("cores")),mp.cpu_count()-1)
        tile_provider.drop_dump(arguments["csv_dump"],layer,cores)
        dump_list = os.listdir(arguments["csv_dump"])
        p = mp.Pool(processes=cores)
        pooled_function = partial(process_tile,arguments=arguments,prepipe=config.get("preprocessing_pipeline"),config=config)
        p.map(pooled_function, dump_list)  
    if config.get("postprocessing_active")=="active":
        analyse_graph(cellobject_thread.exit_and_get_cellgraph(),arguments,config)

if __name__ == '__main__':
    start = time.time()
    initialize_javabridge()
    config = Config.Config()
    in_path = config.get("input_path")
    if config.get("imageanalysis_active")=="active":
        if os.path.isdir(in_path):
            for file in os.listdir(in_path):
                file = in_path+file
                if os.path.isfile(file):
                    analyse_image(file,config)
        if os.path.isfile(in_path):
            analyse_image(in_path,config)
    if config.get("evaluation_active")=="active":
        evaluate_image(config)
    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Image analysis took "+("{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)))
    jv.kill_vm() 