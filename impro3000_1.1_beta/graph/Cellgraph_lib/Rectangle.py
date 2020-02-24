# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 15:17:47 2018

@author: patri
"""

class Rectangle:
    __borderPoints = []
    min_x = 1000000
    min_y = 1000000
    max_x = 0
    max_y = 0
    
    def __init__(self,point1,point2,point3,point4):
        self.__borderPoints = [point1,point2,point3,point4]
        self.__initBoundingBox()
    
    def contains_Point(self,point):
        if self.__fastCheck(point):
            if self.__detailedCheck(point):
                return True
            else:
                return False
        else:
            return False       
        
    def intersect(self, rectangle):
        if self.min_x > rectangle.max_x or self.max_x < rectangle.min_x:
            return False
        if self.min_y > rectangle.max_y or self.max_y < rectangle.min_y:
            return False
        return True
    
    def reload(self,point1,point2,point3,point4):
        self.__borderPoints = [point1,point2,point3,point4]
        self.__initBoundingBox()
    
    def __detailedCheck(self,point):
        n = len(self.__borderPoints)
        inside = False
        p1x,p1y = self.__borderPoints[0]
        for i in range(n+1):
            p2x,p2y = self.__borderPoints[i % n]
            if point[1] > min(p1y,p2y):
                if point[1] <= max(p1y,p2y):
                    if point[0] <= max(p1x,p2x):
                        if p1y != p2y:
                            xints = (point[1]-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or point[0] <= xints:
                            inside = not inside
            p1x,p1y = p2x,p2y    
        return inside
    
    def __fastCheck(self,point):
        if point[0] > self.min_x and point[0] < self.max_x and point[1] > self.min_y and point[1] < self.max_y:
            return True
        else:
            return False
            
    def __initBoundingBox(self):
        minX = 1000000
        minY = 1000000
        maxX = 0
        maxY = 0
        for point in self.__borderPoints:
            minX = min(minX,point[0])
            minY = min(minY,point[1])
            maxX = max(maxX,point[0])
            maxY = max(maxY,point[1])
        self.min_x = minX
        self.min_y = minY
        self.max_x = maxX
        self.max_y = maxY