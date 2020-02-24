#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 17:16:27 2017

@author: patrick
"""

import numpy as np
import math
from Follicle_detector_lib import image_operations as iO

def calculateAutoIntensityThreshold(xPlot,yPlot):
    """
    The function calculates a box plot for given lists of intensity values. The threshold
    is based on most significant jumps between adjacent boundary points.
    @type xPlot: ArrayList
    @param xPlot: List of mean intensity values in x direction
    @type yPlot: ArrayList
    @param yPlot: List of mean intensity values in y-direction
    @rtype: Float
    @return: Intensity threshold for the edge detection
    """
    points = iO.pointsForThreshold(xPlot,yPlot)
    lowerQuartile = np.percentile(np.array(points),25)
    upperQuartile = np.percentile(np.array(points),75)
    iqr = upperQuartile - lowerQuartile
    threshold = upperQuartile + 1.5*iqr
    return threshold

def createMeanX(image,row):
    """
    The function calculates the mean intensity values per column with a height equal to row
    for an image in x direction. The function calculates the mean values for 
    every x value with a distance of row/2 in y-direction in x direction.
    @type image: ArrayList
    @param image: Image, containing the in the intesity values
    @type row: Integer
    @param row: Height of the column
    @rtype: ArrayList
    @return: Mean intensity values of the columns
    """
    xPlot = []
    counter = 0
    for y in range (0,image.shape[0]-row,int(row/2)):
       xPlot.append([])
       for x in range (0,image.shape[1]-1,1):
           xPlot[counter].append(meanX(x,y,image,row))
       counter += 1
    return xPlot

def createMeanY(image,row):
    """
    The function calculates the mean intensity values per row with a width equal to row
    for an image in y-direction. The function calculates the mean values for 
    every y value with a distance of row/2 in x direction in y-direction.
    @type image: ArrayList
    @param image: Image, containing the in the intesity values
    @type row: Integer
    @param row: Width of the row
    @rtype: ArrayList
    @return: Mean intensity values of the rows
    """
    yPlot = []
    counter = 0
    for x in range (0,image.shape[1]-row,(row//2)):
       yPlot.append([])
       for y in range (0,image.shape[0]-1,1):
           yPlot[counter].append(meanY(x,y,image,row))
       counter += 1
    return yPlot

def meanX(x,y,image,row):
    """
    The function calculates the mean intensity value for a column in x direction.
    @type x: Integer
    @param x: x value for the anchoring point of the row
    @type y: Integer
    @param y: y value for the anchoring point of the row
    @type image: ArrayList
    @param image: Image, containing the in the intesity values
    @type row: Integer
    @param row: Height of the column
    @rtype: Float
    @return: Mean intensity value of the column
    """
    meanVal = 0
    count   = 1
    for i in range(y,y+row):
        meanVal  = meanVal+(image[i,x]-meanVal)/count
        count+=1
    return meanVal

def meanY(x,y,image,row):
    """
    The function calculates the mean intensity value for a row in y-direction.
    @type x: Integer
    @param x: x value for the anchoring point of the row
    @type y: Integer
    @param y: y value for the anchoring point of the row
    @type image: ArrayList
    @param image: Image, containing the in the intesity values
    @type row: Integer
    @param row: Width of the row
    @rtype: Float
    @return: Mean intensity value of the row
    """
    meanVal = 0
    count   = 1
    for i in range(x,x+row):
        meanVal  = meanVal+(image[y,i]-meanVal)/count
        count+=1
    return meanVal

def meanBox(startX,startY,width,height,image):
    """
    The function calculates the mean value for a box of intensity values.
    @type startX: Integer
    @param startX: Upper left x value of the box
    @type startY: Integer
    @param startY: Upper left y value of the box
    @type image: ArrayList
    @param image: Image, containing the in the intesity values
    @type width: Integer
    @param width: Width of box
    @type height: Integer
    @param height: Height of the row
    @rtype: Float
    @return: Mean intensity value of the box
    """
    meanVal = 0
    count   = 1
    for x in range(startX,startX+width):
        for y in range(startY,startY+height):
            meanVal  = meanVal+(image[y,x]-meanVal)/count
            count+=1
    return meanVal

def mergeList(array):
    """
    The function merges down a list with a depth of 3 to a list with a depth of 2.
    @type array: ArrayList
    @param array: ArrayList with boundary points
    @rtype: ArrayList
    @return: Merged list
    """
    merged = []
    it = 0
    for i in array:
        merged.append([])
        for k in i:
            for l in k:
                merged[it].append(l)
        it += 1
    return merged

def convertPoints(edges):
    """
    The function converts a list of points of type integer to a list of points
    of type float.
    @type edges: ArrayList
    @param edges: ArrayList with boundary points
    @rtype: ArrayList
    @return: Converted list
    """
    output = []
    for i in edges:
        tmp = []
        for k in i:
            tmp2 = []
            tmp2.append(float(k[0]))
            tmp2.append(float(k[1]))
            tmp.append(tmp2)
        output.append(np.array(tmp))
    return output

def collectAndReconvert(hull,edges,gcNumber):
    """
    The function converts a list of points of type float to a list of points
    of type integer and reorganizes them in single lists per convex hull.
    @type edges: ArrayList
    @param edges: ArrayList with boundary points, with single lists per convex hull
    @type hull: Convex hull
    @param hull: Calculated convex Hull
    @type gcNumber: Integer
    @param gcNumber: Pointer on the current list of points inside the whole edge list
    @rtype: ArrayList
    @return: Converted and collected list
    """
    collector = []
    for i in hull.vertices:
        collector.append((int(edges[gcNumber][i][0]),int(edges[gcNumber][i][1])))
    return collector

def getMajorAxis(points):
    majoraxis = 0
    for point in points:
        for point2 in points:
            distance = math.sqrt(((point2[0]-point[0])**2)+((point2[1]-point[1])**2))
            majoraxis = max(majoraxis,distance)
    return majoraxis

def getMinorAxis(majoraxis,area):
    return 2*(area/((majoraxis/2)*math.pi))

def getEccentricity(points,area):
    majoraxis = getMajorAxis(points)
    minoraxis = getMinorAxis(majoraxis,area)
    eccentricity = math.sqrt((1-(minoraxis**2)/(majoraxis**2)))
    return eccentricity