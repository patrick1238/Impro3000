# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 14:43:55 2018

@author: patri
"""
import numpy as np

def __log_transform(array): 
    """
    Function for the logarithmic transformation of the intensity values.
    @type image: ArrayList
    @param image: Image, which has to be transformed    
    @rtype: 
        ArrayList
    @return: 
        Image, which had to be transformed
    """
    array.astype(float)
    val = 0
    for y in range(0,len(array),1): 
        for x in range(0,len(array[0]),1): 
            val = np.log2(array[y][x]+1)
            array[y][x] = val
    return array

def __shift(array): 
    """
    Function to shift the logarithmized intensity values.
    @type image: ArrayList
    @param image: Image, which has to be transformed
    @rtype: 
        ArrayList
    @return: 
        Image, which had to be transformed
    """
    minVal = np.amin(array)
    maxVal = np.amax(array)
    for y in range(0,len(array),1): 
        for x in range(0,len(array[0]),1): 
            array[y][x] = ((array[y][x] - minVal)/(maxVal-minVal))*255
    array.astype(int)
    return array

def rescale_intensity_values(array):
    return __shift(__log_transform(array))

def intensity_values_to_byte(data, cmin=None, cmax=None, high=255, low=0):
    if high > 255:
        raise ValueError("`high` should be less than or equal to 255.")
    if low < 0:
        raise ValueError("`low` should be greater than or equal to 0.")
    if high < low:
        raise ValueError("`high` should be greater than or equal to `low`.")

    if cmin is None:
        cmin = data.min()
    if cmax is None:
        cmax = data.max()

    cscale = cmax - cmin
    print(cscale,cmax,cmin)
    if cscale < 0:
        raise ValueError("`cmax` should be larger than `cmin`.")
    elif cscale == 0:
        cscale = 1

    scale = float(high - low) / cscale
    bytedata = (data - cmin) * scale + low
    return (bytedata.clip(low, high) + 0.5).astype(np.uint8)
    
    