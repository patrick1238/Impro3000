# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 15:00:16 2018

@author: patri
"""

class Image():
    
    __id = None
    __name = None
    __array = None
    __x_coord = None
    __y_coord = None
    __layer = None
    __staining = None # [primary_staining, secondary_staining]
    __width = None
    __height = None

    def __init__(self,objectID="unknow", name = None, numpy_array=None, x_coord=None, y_coord=None,width=None,height=None,layer=None,staining=None):
        self.__id = objectID
        self.__name = name
        self.__array = numpy_array
        self.__x_coord = x_coord
        self.__y_coord = y_coord
        self.__layer = layer
        self.__width = width
        self.__height = height
        if isinstance(staining, str):
            self.__staining = staining.split(",")
        else:
            self.__staining = staining
            
    def get_numpy_array(self):
        return self.__array

    
    def set_numpy_array(self, numpy_array):
        self.__array = numpy_array

    def get_staining(self):
        return self.__staining
    
    def set_staining(self, staining):
        self.__staining = staining

    def get_layer(self):
        return self.__layer
    
    def set_layer(self, layer):
        self.__layer = layer
    
    def get_width(self):
        return self.__width
    
    def set_width(self, width):
        self.__width = width

    def get_height(self):
        return self.__height
    
    def set_height(self, height):
        self.__height = height

    def get_global_x(self):
        return self.__x_coord
    
    def set_global_x(self, global_x):
        self.__global_x = global_x

    def get_global_y(self):
        return self.__y_coord
    
    def set_global_y(self, global_y):
        self.__global_y = global_y
    
    def get_id(self):
        return self.__id
    
    def set_id(self, objectID):
        self.__id = objectID
    
    def get_name(self):
        return self.__name
    
    def set_name(self, name):
        self.__name = name
        
    def get_new_instance(self):
        return Image(self.__id,self.__name, self.__array, self.__x_coord, self.__y_coord, self.__width, self.__height,self.__layer,self.__staining)
