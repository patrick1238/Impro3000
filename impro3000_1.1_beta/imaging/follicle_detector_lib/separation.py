#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 18:16:30 2017

@author: patrick
"""

def cross(first,second):
    """
    The function tests the lines between two start and end points for a possible
    intersection.
    @type first: ArrayList
    @param first: List with two points, a start and an end point
    @type second: ArrayList
    @param second: List with two points, a start and an end point
    @rtype: Boolean
    @return: True, if the two lines crossing each other
    """
    if(first[0][0]==first[1][0]):
        pair1 = first
        pair2 = second
    else:
        pair1 = second
        pair2 = first
    x = pair2[0][1]
    y = pair1[0][0]
    if(x >= pair1[0][1] and x <= pair1[1][1] and y >= pair2[0][0] and y <= pair2[1][0]):
        return True
    else:
        return False

def checkCurGC(array,pair):
    """
    The function tests a set of multiple start and end points for any intersections
    with a given start and end point.
    @type array: ArrayList
    @param array: Set of multiple start and end points
    @type pair: ArrayList
    @param pair: List with two points, a start and an end point
    @rtype: Boolean
    @return: True, if the pair has any intersections with the given array
    """
    inside = False
    for i in range(0,len(array),2):
        test = cross(pair,(array[i],array[i+1]))
        if(test == True):
            inside = True
    return inside

def collectEdges(array):
    """
    The function pools every boundary start and end points in a single list, 
    if the lines between start and end points have intersections to one of the
    other.   
    @type array: ArrayList
    @param array: Set of multiple start and end points
    @rtype: ArrayList, ArrayList
    @return: List with the pooled boundary points, remaining, unpooled points
    """
    collected = [[],[]]
    collector = 1
    collected[0].append(array[0][0])
    collected[0].append(array[0][1])
    del array[0][0]
    del array[0][0]
    save = []
    while(collector>0):
        collector = 0
        for y in range(0,len(array[1]),2):
            test = checkCurGC(collected[0],(array[1][y],array[1][y+1]))
            if(test == True):
                collector += 1
                collected[1].append(array[1][y])
                collected[1].append(array[1][y+1])
                save.append(array[1][y])
                save.append(array[1][y+1])
        while(len(save)>0):
            array[1].remove(save.pop())
        collector = 0
        for x in range(0,len(array[0]),2):
            test = checkCurGC(collected[1],(array[0][x],array[0][x+1]))
            if(test == True):
                collector += 1
                collected[0].append(array[0][x])
                collected[0].append(array[0][x+1])
                save.append(array[0][x])
                save.append(array[0][x+1])
        while(len(save)>0):
            array[0].remove(save.pop())
    return (collected,array)

def gcSeperation(array):
    """
    The function pools every boundary start and end points in a single list, 
    if the lines between start and end points have intersections to one of the
    other. This functions goes over every start and end point in x direction
    and y direction till no points are remaining.
    @type array: ArrayList
    @param array: Set of multiple start and end points
    @rtype: ArrayList
    @return: List with the pooled boundary points
    """
    collected = []
    while(len(array[0])>0 and len(array[1])>0):
        tmp = collectEdges(array)
        array = tmp[1]
        collected.append(tmp[0])
    return collected