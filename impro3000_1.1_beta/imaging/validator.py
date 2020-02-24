# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 15:50:52 2019

@author: patri
"""
import sys
sys.path.append("..")
import mahotas
from imaging.follicle_detector_lib import image_operations as iO
from scipy import ndimage as ndi
import numpy as np
import pandas as pd

def __parseCoordinates(cur_object):
    start = int(cur_object.find("["))+1
    start2 = cur_object.rfind("[")+1
    end = int(cur_object.find("]"))
    end2 = cur_object.rfind("]")
    xcoords = cur_object[start:end].split(",")
    ycoords = cur_object[start2:end2].split(",")
    coordinates = []
    for i in range(0,len(xcoords)):
        coordinates.append((int(ycoords[i]),int(xcoords[i])))
    return coordinates

def __createValidationImage(image,file_name,annotation_folder):
    validationImage = iO.createDefault(image)
    validationFile = open(annotation_folder+file_name + "_AktinChannel.csv","r")
    validationFile.readline()
    for cur_object in validationFile:
        coordinates = __parseCoordinates(cur_object)
        mahotas.polygon.fill_polygon(coordinates,validationImage)
    return validationImage

def __calculateOverlapCoefficents(resultsImage,validationImage):
    tpsPixel = resultsImage+validationImage
    tpsPixel[np.where(tpsPixel<2)] = 0
    tps = np.count_nonzero(tpsPixel)
    fpsPixel = resultsImage-validationImage
    fpsPixel[np.where(fpsPixel<0)] = 0
    fps = np.count_nonzero(fpsPixel)
    fnsPixel = validationImage-resultsImage
    fnsPixel[np.where(fnsPixel<0)] = 0
    fns = np.count_nonzero(fnsPixel)
    precision = tps / (tps + fps)
    recall = tps / (tps+fns)
    fFactor = 2*(precision*recall)/(precision+recall)
    zijdenbos = (2 * tps)/(np.count_nonzero(resultsImage)+np.count_nonzero(validationImage))
    results = {"Precision_PB":precision,"Recall_PB":recall,"FFactor_PB":fFactor,"ZSI":zijdenbos}
    return results

def validate_results(mask,file_name,validation_folder,arguments,objects=None,save=False):
    com = []
    if objects==None:
        mask_labeled, mask_num = ndi.label(mask)
        com = ndi.measurements.center_of_mass(mask, mask_labeled, range(1, mask_num+1))
    else:
        for object_id,properties in objects.items():
            com.append((properties["y"],properties["x"]))
    validation_image = __createValidationImage(mask,file_name,validation_folder)
    results=__calculateOverlapCoefficents(mask,validation_image)
    tpsResults = 0
    tps = 0
    fps = 0
    fns = 0
    validation_image.astype(int)
    mask.astype(int)
    val_labeled, val_num = ndi.label(validation_image)
    centers_val = ndi.measurements.center_of_mass(validation_image, val_labeled, range(1, val_num+1))
    for center in centers_val:
        y = int(round(center[0]))
        x = int(round(center[1]))
        if mask[y][x] == 0.0:
            fns += 1
        else:
            tps += 1
    for center in com:
        y = int(round(center[0]))
        x = int(round(center[1]))
        if validation_image[y][x] == 1.0:
            tpsResults += 1
        else:
            fps += 1
    results["Precision_OB"] = tps / (tps + fps)
    results["Recall_OB"] = tps / (tps+fns)
    results["FFactor_OB"] = 2*(results["Precision_OB"]*results["Recall_OB"])/(results["Precision_OB"]+results["Recall_OB"])          
    if save:
        df = pd.DataFrame.from_dict({file_name:results}, orient="index")
        df.to_csv(arguments["results"]+"validation_results.csv")
    return results
    