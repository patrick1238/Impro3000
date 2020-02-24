 #!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on Thu Mar  9 12:38:19 2017

@author: Patrick Wurzel
         Matrikelnummer: 46728546
         E-Mail: p.wurzel@bioinformatik.uni-frankfurt.de
"""

import sys
sys.path.append("./Follicle_detector_lib/")
import Follicle_detector_lib.basic_operations as bO
import Follicle_detector_lib.image_operations as iO
import Follicle_detector_lib.seperation as se
import time
import Follicle_detector_lib.math_operations as mlO
import copy
import multiprocessing as mp
import numpy as np
import math
import scipy

def detect(Actin_channel_image,arguments):
    """
    Main function to provide the pipeline for germinal center detection.
    @type args: ArrayList
    @param args: Commandline arguments
    """
    
    row = 10 #Width of the row for the mean calculation
    whiteThresholdTest = 180 #Minimum intensity inside a germinal center
    roiDimensionTest = 1000 #Dimension of the box, for the mean intesity calculation, which is the basis to discriminate between foreground and background (width = width/dimension, height = height/dimension)
    sigmaVal = 4 #Sigma value for the gaussian filter
    kernelSize = 8 #Kernel size for the closing operation
    lowerBoundary = 15 #Smallest part width or height of a germinal center in pixel, which will be accepted within the edge detection
    upperBoundary = 230 #Biggest width or height of a germinal center in pixel, which will be accepted within the edge detection
    formFactorThreshold = 0.7
    eccentricityThreshold = 0.95
    areaMax = 42000
    areaMin = 350
    maxLayer = 3 #Maximal layer of the given svs image
    roiThresholdTest = 240 #Threshold to discriminate between Fore- and Background
    averageIntensity = 216 #Average intensity inside the image, the values were fixed for
    
    pool = mp.Pool(processes=mp.cpu_count()-1)
    print("Starttime: " + str(time.ctime()))
    workingDir = arguments["tmp"]
    image = ~np.array(Actin_channel_image.get_numpy_array())
    print("####################"+str(np.average(image)))
    scalingfactor = (round(np.average(image))/averageIntensity)**0
    whiteThreshold = min(int(whiteThresholdTest *(math.sqrt(scalingfactor))),250)
    roiThreshold = min(int(roiThresholdTest *math.sqrt(scalingfactor)),240)
    roiDimension = int(roiDimensionTest*((2-scalingfactor)**2))
    print(str(time.ctime()))
    print("Step: Preprocessing incl. ROI detection")
    roi = iO.calculateROI(image,roiDimension,workingDir,roiThreshold)

    image = bO.preprocess(workingDir,image,sigmaVal,kernelSize)
    print(str(time.ctime()))
    print("Step: Calculating (overlapping) mean Values")
    xPlot = mlO.createMeanX(image, row)
    yPlot = mlO.createMeanY(image, row)
    print(str(time.ctime()))
    print("Step: Shockfilter x axes")
    xPlot = iO.startShockFilterPooled(xPlot,pool)
    print(str(time.ctime()))
    print("Step: Shockfilter y axes")
    yPlot = iO.startShockFilterPooled(yPlot,pool)
    pool.close()
    print(str(time.ctime()))
    print("Step: Edge detection")
    threshold = mlO.calculateAutoIntensityThreshold(xPlot,yPlot)
    possibleEdges = iO.edgeDetection(xPlot,yPlot,row,threshold,whiteThreshold,roi,lowerBoundary,upperBoundary)
    imageTest1 = copy.deepcopy(image)
    bO.markEdges(imageTest1,possibleEdges,workingDir,2)
    print(str(time.ctime()))
    print("Step: GC partitioning")
    possibleEdges = se.gcSeperation(possibleEdges)
    possibleEdges = mlO.mergeList(possibleEdges)
    imageTest2 = copy.deepcopy(image)
    bO.markEdges(imageTest2,possibleEdges,workingDir,1)
    print(str(time.ctime()))
    print("Step: Calculating convex hulls")
    edges,centerOfMasses = iO.getConvexHull(possibleEdges,formFactorThreshold,eccentricityThreshold,areaMin,areaMax)
    print("Step: Building mask")
    return iO.createMask(image,maxLayer,edges,arguments["results"])