# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 14:19:58 2019

@author: patri
"""

import sys
sys.path.append("..")
import imaging.color_deconvolution as cd

def main(image,arguments):
    cd30,hem = cd.colour_deconvolution(image)