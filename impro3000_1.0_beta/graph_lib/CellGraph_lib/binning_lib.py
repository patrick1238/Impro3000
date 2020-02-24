# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 13:48:10 2018

@author: patri
"""

import graph_lib.CellGraph_lib.Rectangle as rect

__binSize = 1000

def __get_graph_width(cellgraph):
    nodes = cellgraph.get_nodes()
    maxX = 0
    for key in nodes:
        maxX = max(maxX,nodes[key][0])
    return maxX+1

def __get_graph_height(cellgraph):
    nodes = cellgraph.get_nodes()
    maxY = 0
    for key in nodes:
        maxY = max(maxY,nodes[key][1])
    return maxY+1

def bin_cellgraph(cellgraph):
    width = __get_graph_width(cellgraph)
    height = __get_graph_height(cellgraph)
    binnedCoordinates = [[[]for x in range(int(width/__binSize)+2)]for y in range(int(height/__binSize)+2)]
    nodes = cellgraph.get_nodes()
    for key in nodes:
        x = int((nodes[key][0])/__binSize)
        y = int((nodes[key][1])/__binSize)
        binnedCoordinates[y][x].append(key)
    return binnedCoordinates

def get_corresponding_bins(x,y,binned):
    bins = []
    bins += binned[y][x]
    if y < len(binned)-1:
        bins+=binned[y+1][x]
        if x > 0:
            bins += binned[y+1][x-1]
        if x < len(binned[y])-1:
            bins+=binned[y+1][x+1]
    if x < len(binned[y])-1:
        bins+=binned[y][x+1]
    return bins

def getCommunicationAreaBins(point1,point2,area,binned):
    bins = []
    communicationAreaBins = []
    communicationAreaBins = __getBinsOnePoint(point1,area,binned)
    communicationAreaBins = list(set(communicationAreaBins + __getBinsOnePoint(point2,area,binned)))
    for coords in communicationAreaBins:
        bins += binned[coords[1]][coords[0]]
    return bins
    
def __getBinsOnePoint( point, area, binned):
    currentBins = []
    x = int(point[0]/__binSize)
    y = int(point[1]/__binSize)
    height = len(binned)
    width = len(binned[y])
    curBin = rect.Rectangle((0,0),(0,0),(0,0),(0,0))
    for xbin in range(-1,2):
        newX = x + xbin
        for ybin in range(-1,2):
            newY = y + ybin
            if newX >= 0 and newY >= 0 and newX < width and newY < height:
                curBin.reload((newX*__binSize,newY*__binSize),(((newX+1)*__binSize)-1,newY*__binSize),(((newX+1)*__binSize)-1,((newY+1)*__binSize)-1),(newX*__binSize,((newY+1)*__binSize)-1))
                if area.intersect(curBin):
                    currentBins.append((newX,newY))
    return currentBins