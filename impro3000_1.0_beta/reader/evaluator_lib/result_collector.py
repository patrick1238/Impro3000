# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 13:28:21 2019

@author: patri
"""

import os
import fnmatch, re
import sys
sys.path.append("..")
import evaluator_lib.disease_container as di_container
import copy
import numpy as np

def collect_result_files_for_visualization(path,diagnosis_list=None):
    # Get the list of all files in directory tree at given path
    list_of_files = {}
    list_of_files = __get_list_of_files(path)
    return __order_for_disease(list_of_files,diagnosis_list)

def collect_result_files_for_training(path,diagnosis_list=None):
    list_of_files = {}
    list_of_files = __get_list_of_files(path)
    return __create_dataframe(list_of_files,diagnosis_list)

def reorder_by_feature(disease_containers):
    common_features = __get_features_in_common(disease_containers)
    output = []
    for feature in common_features:
        results = {}
        for disease in disease_containers:
            results[disease] = disease_containers[disease].get(feature)
        output.append((feature,__type_converter(results)))
    return output

def __type_converter(dictionary):
    for key in dictionary:
        dictionary[key] = np.array(dictionary[key]).astype(float)
    return dictionary
    
def __get_features_in_common(disease_containers):
    cur = copy.deepcopy(disease_containers)
    disease,first_container = cur.popitem()
    result = set(first_container.get_feature_names())
    for container in cur.values():
        result.intersection_update(container.get_feature_names())
    return result
    
def __order_for_disease(listOfFiles,diagnosis_list=None):
    container = {}
    if diagnosis_list != None:
        diagnosis = __read_diagnosis_file(diagnosis_list)
        for file in listOfFiles:
            identifier = os.path.basename(file).split(".")[0]
            if identifier in diagnosis:
                if diagnosis[identifier] in container:
                    container[diagnosis[identifier]].add_case(identifier,file)
                else:
                    container_obj = di_container.disease_container(diagnosis[identifier])
                    container_obj.add_case(identifier,file)
                    container[diagnosis[identifier]] = container_obj
    return container
        
def __create_dataframe(listOfFiles,diagnosis_list=None):
    container = {}
    if diagnosis_list != None:
        diagnosis = __read_diagnosis_file(diagnosis_list)
        for file in listOfFiles:
            result_file = open(file)
            header = result_file.readline().strip("\n").split(",")
            results = result_file.readline().strip("\n").split(",")
            dictionary = dict(zip(header,results))
            identifier = dictionary["identifier"]
            dictionary["disease"] = diagnosis[identifier]
            del dictionary["identifier"]
            container[identifier] = dictionary
    return container

def __read_diagnosis_file(path):
    diagnosis = {}
    file = open(path)
    for line in file:
        splitted = line.strip("\n").split(",")
        diagnosis[splitted[0]] = splitted[1]
    return diagnosis

def __get_list_of_files(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = []
    regex = fnmatch.translate('*.ima')
    reobj = re.compile(regex)
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + __get_list_of_files(fullPath)
        else:
            if reobj.match(fullPath):
                allFiles.append(fullPath)
    return allFiles  