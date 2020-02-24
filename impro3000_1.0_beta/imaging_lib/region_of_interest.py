# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 11:05:18 2018

@author: patri
"""

import numpy as np
from scipy import ndimage

__SCRIPT_NAME="[Region of interest]"

def rgb2gray(image):
    out_image = []
    index = 0
    for line in image:
        out_image.append([])
        for pixel in line:
            out_image[index].append(int((sum(pixel)/3)))
        index = index + 1
    return out_image

def createDefault(image):
    """
    Function to create a black image with the same scale like a given image.
    @type image: ArrayList
    @param image: Template for the creation of a black copy
    @rtype: 
        ArrayList
    @return: 
        black image with the same scale like a given image
    """
    array = np.zeros(image.shape)
    return array

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
            meanVal  = meanVal+((image[y,x]-meanVal)/count)
            count+=1
    return int(meanVal)

def fillRectangle(x,y,width,height,mask): 
    """
    Function to mark a white box in a given mask.
    @type x: Integer
    @param x: Upper left x value of the starting point for filling the white box
    @type y: Integer
    @param y: Upper left y value of the starting point for filling the white box
    @type width: Integer
    @param width: Width of the box, which has to be filled
    @type height: Integer
    @param height: Height of the box, which has to be filled
    @type mask: ArrayList
    @param mask: Image, in which the box will be filled
    @rtype: ArrayList
    @return: Marked image
    """
    for w in range(x,x+width,1):
        for h in range(y,y+height,1):
            mask[h,w] = 255
    return mask

def calculateROI(image,dimension,workingDir,roiThreshold,identifier="ROI"):
    """
    Function to calculate the regoin of interest(ROI).
    @type dimension: Integer
    @param dimension: Dimension of the box, for the mean intesity calculation, which
    is the basis to discriminate between foreground and background
    (width = width/dimension, height = height/dimension)
    @type image: ArrayList
    @param image: Image, which is the basis for the ROI calculation
    @type workingDir: String
    @param workingDir:Path to the current working directory 
    @rtype: ArrayList
    @return: Image with the marked ROI
    """
    print(__SCRIPT_NAME+": Calculating Region of interest")
    if len(image.shape) > 2:
        image = rgb2gray(image)
    image = ndimage.filters.gaussian_filter(image,5)
    x_length = image.shape[1]
    y_length = image.shape[0]
    boxWidth = int(max(x_length/dimension,1))
    boxHeight = int(max(y_length/dimension,1))
    xBorder = x_length%boxWidth
    yBorder = y_length%boxHeight
    mask = createDefault(image)
    threshold = roiThreshold
    for x in range(0,x_length-xBorder,boxWidth): 
        for y in range(0,y_length-yBorder,boxHeight): 
            meanVal = meanBox(x,y,boxWidth,boxHeight,image)
            if meanVal < threshold: 
                mask = fillRectangle(x,y,boxWidth,boxHeight,mask)
    if(xBorder>0): 
        for y in range(0,y_length-yBorder,boxHeight): 
            meanVal = meanBox(x_length-xBorder,y,xBorder,boxHeight,image)
            if meanVal < threshold: 
                mask = fillRectangle(x_length-xBorder,y,xBorder,boxHeight,mask)
    if(yBorder>0): 
        for x in range(0,x_length-xBorder,boxWidth): 
            meanVal = meanBox(x,y_length-yBorder,boxWidth,yBorder,image)
            if meanVal < threshold: 
                mask = fillRectangle(x,y_length-yBorder,boxWidth,yBorder,mask)
    if(xBorder>0 and yBorder>0): 
        meanVal = meanBox(x_length-xBorder,y_length-yBorder,xBorder,yBorder,image)
        if meanVal < threshold: 
            mask = fillRectangle(x_length-xBorder,y_length-yBorder,xBorder,yBorder,mask)
    mask = ndimage.binary_closing(mask)
    filled = ndimage.binary_fill_holes(mask)
    filled = filled * 1
    return filled