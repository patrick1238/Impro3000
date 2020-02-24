 #!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on Thu Mar  9 12:38:19 2017

@author: Patrick Wurzel
         Matrikelnummer: 46728546
         E-Mail: p.wurzel@bioinformatik.uni-frankfurt.de
"""

import sys
sys.path.append("..")
from imaging.follicle_detector_lib import image_operations as iO
from imaging.follicle_detector_lib import separation as se
from imaging.follicle_detector_lib import math_operations as mlO
from imaging import roi_detector
import time
import multiprocessing as mp
import numpy as np
import math
from scipy import misc

def detect(Actin_channel_image,roi,arguments):
    """
    Main function to provide the pipeline for germinal center detection.
    @type args: ArrayList
    @param args: Commandline arguments
    """
    
    row = 10 #Width of the row for the mean calculation
    whiteThreshold = 225 #Minimum intensity inside a germinal center
    sigmaVal = 4 #Sigma value for the gaussian filter
    kernelSize = 8 #Kernel size for the closing operation
    lowerBoundary = 20 #Smallest part width or height of a germinal center in pixel, which will be accepted within the edge detection
    upperBoundary = 160 #Biggest width or height of a germinal center in pixel, which will be accepted within the edge detection
    formFactorThreshold = 0.9
    eccentricityThreshold = 0.95
    areaMax = 23000
    areaMin = 300
    averageIntensity = 217 #Average intensity inside the image, the values were fixed for
    __SCRIPT_NAME="[Follicle detection]"
    
    pool = mp.Pool(processes=mp.cpu_count()-1)
    workingDir = arguments["tmp"]
    image = ~np.array(Actin_channel_image.get_numpy_array())

    scalingfactor = (round(np.average(image))/averageIntensity)
    whiteThreshold = min(int(whiteThreshold *(math.sqrt(scalingfactor))),250)
    #whiteThreshold = round(np.average(image))


    print(round(np.average(image)),whiteThreshold)
    print(str(time.ctime()))
    print(__SCRIPT_NAME+": Preprocessing")
    image = iO.preprocess(workingDir,image,sigmaVal,kernelSize)
    print(str(time.ctime()))
    print(__SCRIPT_NAME+": Calculating (overlapping) mean Values")
    xPlot = mlO.createMeanX(image, row)
    yPlot = mlO.createMeanY(image, row)
    print(str(time.ctime()))
    print(__SCRIPT_NAME+": Shockfilter")
    xPlot = iO.startShockFilterPooled(xPlot,pool)
    yPlot = iO.startShockFilterPooled(yPlot,pool)
    pool.close()
    print(str(time.ctime()))
    print(__SCRIPT_NAME+": Edge detection")
    threshold = mlO.calculateAutoIntensityThreshold(xPlot,yPlot)
    possibleEdges = iO.edgeDetection(xPlot,yPlot,row,threshold,whiteThreshold,roi,lowerBoundary,upperBoundary)
    print(str(time.ctime()))
    print(__SCRIPT_NAME+": GC partitioning")
    possibleEdges = se.gcSeperation(possibleEdges)
    possibleEdges = mlO.mergeList(possibleEdges)
    print(str(time.ctime()))
    print(__SCRIPT_NAME+": Calculating convex hulls")
    edges,centerOfMasses = iO.getConvexHull(possibleEdges,formFactorThreshold,eccentricityThreshold,areaMin,areaMax)
    print(str(time.ctime()))
    print(__SCRIPT_NAME+": Building mask")
    return iO.createMask(image,edges,arguments["results"]),centerOfMasses