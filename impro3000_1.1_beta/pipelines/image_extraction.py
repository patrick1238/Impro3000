# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 17:18:50 2019

@author: Hodgkin
"""

from scipy import misc

def main(image,arguments):
    misc.imsave(arguments["results"]+image.get_name()+"_"+image.get_id()+".png",image.get_numpy_array())