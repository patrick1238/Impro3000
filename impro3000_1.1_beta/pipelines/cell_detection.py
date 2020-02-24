# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 17:19:16 2019

@author: Hodgkin
"""

import sys
sys.path.append("..")
from reader.std_pckgs import Config
from imaging import cd30_cell_detector

def main(image,arguments):
    config = Config.Config(parse_cmd=False)
    cells,segmented = cd30_cell_detector.detect(image,config,arguments,True)