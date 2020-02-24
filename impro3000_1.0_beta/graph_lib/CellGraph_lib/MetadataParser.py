# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 14:00:09 2018

@author: patri
"""
from io import open

def parseMetadata(path):
    metadata = {}
    with open(path,'r',encoding='UTF-8') as src:
        for line in src:
            if len(line) == 0: break #happens at end of file, then stop loop
            if "##" in line:
                lineSplitted = line.split(":")
                metadata.update({lineSplitted[0].strip("##"):lineSplitted[1].strip("\n")})
    return metadata