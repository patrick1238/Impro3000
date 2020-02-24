# -*- coding: utf-8 -*-

import numpy as np
import math

class TileProvider():
    
    image_tile_coordinates = None
    wsi_object = None

    def __init__(self, wsi_object):
        self.wsi_object = wsi_object
        self.image_tile_coordinates = {} # access: image_tile_coordinates["layer3"] 
    
    def filter_list_for_roi(self,coords,layer,roi,resize):
        drop = []
        for key in coords:
            value = coords[key]            
            x = math.floor(value[0]/resize)
            y = math.floor(value[1]/resize)
            width = math.ceil(value[2]/resize)
            height = math.ceil(value[3]/resize)
            widthroi = len(roi[0])
            heightroi = len(roi)
            x = max(0,x)
            y = max(0,y)
            width = min(width,widthroi-x)
            height = min(height,heightroi-y)
            subarray = roi[y:y+height,x:x+width]
            if np.count_nonzero(subarray) == 0:
                drop.append(key)
        for key in drop:
                coords.pop(key)
        return coords
    
    def calc_image_tiles(self, layer=0, roi=[], tile_size=3072, overlap=100, resize=32):
        width = self.wsi_object.get_width(layer)
        height = self.wsi_object.get_height(layer)
        coords = {}
        x_count = 0
        y_count = 0
        x_value = 0
        y_value = 0
        while (y_value+tile_size)<height:
            while(x_value+tile_size)<width:
                coords[str(layer)+"_"+str(x_count)+"_"+str(y_count)] = (x_value,y_value,tile_size,tile_size)
                x_value = x_value + tile_size - overlap
                x_count = x_count + 1
            coords[str(layer)+"_"+str(x_count)+"_"+str(y_count)] = (x_value,y_value,width-x_value,tile_size)
            x_value = 0
            x_count = 0
            y_count = y_count + 1
            y_value = y_value + tile_size - overlap
        while(x_value+tile_size)<width:
            coords[str(layer)+"_"+str(x_count)+"_"+str(y_count)] = (x_value,y_value,tile_size,height-y_value)
            x_value = x_value + tile_size - overlap
            x_count = x_count + 1
        coords[str(layer)+"_"+str(x_count)+"_"+str(y_count)] = (x_value,y_value,width-x_value,height-y_value)
        if len(roi)>0:
            coords = self.filter_list_for_roi(coords,layer,roi,resize)
        self.image_tile_coordinates[layer] = coords        
    
    def divide_image_tiles(self,image_tile_dict,cores):
        sub_length_temp = len(image_tile_dict) / cores
        sub_length = int(sub_length_temp)
        counter = 0
        pointer = 0
        sublists = [[]]
        for key in image_tile_dict:
           if counter > sub_length:
               counter = 0
               pointer = pointer + 1
               sublists.append([])
           output = str(key)+","+str(image_tile_dict[key]).replace("(","").replace(")","").replace("[","").replace("]","")
           sublists[pointer].append(output)
           counter += 1
        return sublists
            
    
    def drop_dump(self, dump_path=None, layer=0, cores=1):
        """ saves the tile_sublists as csv files. """
        # seperate tile_list into 
        image_tile_list = self.image_tile_coordinates[layer]
        image_tile_sub_lists = self.divide_image_tiles(image_tile_list, cores)
        # dump all sublists:
        for sub_list in image_tile_sub_lists:
            counter = image_tile_sub_lists.index(sub_list)
            csv_file_path = dump_path + "tile_sublist_no_" + str(counter) + ".csv"
            f = open(csv_file_path,"w")
            for image_string in sub_list:
                f.write(image_string+"\n")
            f.close()









