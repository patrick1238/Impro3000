# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 09:52:29 2019

@author: patri
"""
from pathlib import Path
import os
import pandas as pd
import numpy as np

def convert_length_to_pixel(values,resolution):
    converted = []
    for value in values:
        pixel_value = int(round(float(value)/resolution))
        converted.append(pixel_value)
    return converted

def convert_position_to_local_pixel(values,resolution):
    np_array = np.array(values)
    min_value = np_array.min()
    normalized = []
    for value in values:
        new_value = value - min_value
        pixel_value = int(round(float(new_value)/resolution))
        normalized.append(pixel_value)
    return normalized

def finalize_and_save_case_as_csv(case_id,case,outpath,resolution):
    single_case = {}
    single_case["ID"] = []
    for object_id in case:
        single_case["ID"].append(object_id)
        for object_property in case[object_id]:
            if object_property not in single_case:
                single_case[object_property] = []
            single_case[object_property].append(case[object_id][object_property])
    for key in single_case:
        if "Position" in key:
            single_case[key] = convert_position_to_local_pixel(single_case[key],resolution)   
        if "Ellipsoid Axis Length" in key:
            single_case[key] = convert_length_to_pixel(single_case[key],resolution)
    column_names = list(single_case.keys())
    df = pd.DataFrame(single_case, columns= column_names)
    df.to_csv (outpath+case_id+".csv", index = None, header=True)

def identify_stain(entry):
    return entry.split(" ")[0]

def identify_case(entry):
    splitted = entry.split("_")
    case = splitted[0]
    if "-" not in case:
        case = case + "-" + splitted[1]
    counter = 0
    for path_part in splitted:
        if "ii" in path_part:
            case = case + "_" + path_part.replace("[","")
        if "Region" in path_part or "TileScan" in path_part:
            if " " in path_part:
                case = case + "_" + path_part.replace(" ","-")
            else:
                case = case + "_" + splitted[counter] + "-" + splitted[counter+1]
            break
        counter = counter + 1
    return case

def analyse_line(line,cases,columns,header):
    header_single = header.split(",")
    entries = line.split(",")
    case = identify_case(entries[columns["image_name"][0]])       
    object_id = entries[columns["object_id"][0]]
    stain = identify_stain(entries[columns["stain"][0]])
    if case not in cases:
        cases[case] = {}
    if object_id not in cases[case]:
        cases[case][object_id] = {"stain": stain}
    for property_column in columns["properties"]:
        cases[case][object_id][header_single[property_column]] = float(entries[property_column])
    return cases
    

def identify_valuable_colums(header):
    columns = {"properties": [],"object_id": [], "stain": [], "image_name": [] }
    header_single = header.split(",")
    stopper = False
    counter = 0
    for head in header_single:
        if head == "Unit":
            stopper = True
        elif not stopper:
            columns["properties"].append(counter)
        elif head == "OriginalID":
            columns["object_id"].append(counter)
        elif head == "Original Component Name":
            columns["stain"].append(counter)
        elif head == "Original Image Name":
            columns["image_name"].append(counter)
        counter = counter + 1
    return columns

def analyse_file(file_path, cases):
    with open(file_path, "r") as file:
        for i in range(3):
            file.readline()
        header = file.readline()
        valuable_columns = identify_valuable_colums(header)
        for line in file.readlines():
            cases = analyse_line(line,cases,valuable_columns,header)
    return cases

def convert_batch_folder(path,config):
    folders = os.listdir(path)
    outpath = path + "impro3000_graph_tmp_folder/"
    file = Path(outpath)
    if not file.is_dir():
        os.makedirs(outpath)
    cases = {}
    config.set_value("input_path",outpath)
    features_to_analyse = config.get("batched_features").split(",")
    for folder in folders:
        files = os.listdir(path + folder)
        for file in files:
            for feature in features_to_analyse:
                if feature in file:
                    cases = analyse_file(path + folder + "/" + file,cases)
    for case in cases:
        finalize_and_save_case_as_csv(case,cases[case],outpath,float(config.get("resolution")))
    return outpath, config