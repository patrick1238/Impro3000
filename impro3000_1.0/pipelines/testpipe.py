# -*- coding: utf-8 -*-
from scipy import misc
import sys
sys.path.append("..")
from imaging import cd30_cell_detector
from reader.WSI_reader_lib import Config

def main(image,arguments):
    config = Config.Config(parse_cmd=False)
    cells = cd30_cell_detector.detect(image,config,arguments)

    