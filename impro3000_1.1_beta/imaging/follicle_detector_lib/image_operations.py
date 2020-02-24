import sys
sys.path.append("../..")
from imaging.follicle_detector_lib import math_operations as mlO
from scipy import ndimage, misc
from scipy.spatial import ConvexHull
import numpy as np
import mahotas
import math
import gc

def preprocess(workingDir,image,sigmaVal,kernelSize):
    """
    Pipeline to preprocess the image.
    The preprocessing steps are gaussian filtering, log transformation,
    value shifting and the closing operation.
    @param image: Image, which should be preprocessed
    @type image: ArrayList
    @param sigmaVal: Sigma value for the gaussian filter
    @type sigmaVal: Integer
    @param kernelSize: Kernel size for the closing operation
    @type kernelSize: Integer
    @rtype:
        ArrayList
    @return:
        Image, which has been preprocessed
    """
    image = np.array(gaussian(image,sigmaVal))
    image = np.array(logTransform(image))
    image = np.array(shift(image))
    image = closing(image,kernelSize)
    return image

def shockFilter(curve): 
    """
    Function to perform the Shockfilter n-times on one curve.
    @type curve: ArrayList
    @param curve: List of Values, which has to be flattend
    @rtype: 
        ArrayList
    @return: 
        Filtered List
    """
    iterations = 20
    for i in range(iterations): 
        cur_old_l =  curve[0]
        cur_old   =  curve[0]
        cur_old_r =  curve[1]
        for i in range(1,len(curve)-1): 
            cur_old_l = cur_old
            cur_old = cur_old_r
            cur_old_r = curve[i+1]
            delta = cur_old_r - 2 *cur_old + cur_old_l
            delta_left = cur_old-cur_old_l
            delta_right = cur_old_r-cur_old            
            nabla = min(np.abs(delta_left),np.abs(delta_right))*((np.sign(delta_left)+np.sign(delta_right))/2)
            nabla=-np.sign(delta)*np.abs(nabla)
            curve[i]= curve[i]+nabla
    return curve

def startShockFilterPooled(curves,pool):
    """
    Function to call the shock filter parallelized per list of intensity values of an image: 
    @type curves: ArrayList
    @param curves: List of lists with Values, which has to be flattend
    @type pool: Multiprocessing pool
    @param pool: Pool of processor, the function will work on
    @rtype: 
        ArrayList
    @return: 
        List with Flattend curves
    """
    flattenedCurves = []
    gc.collect()
    #counter = 0
    #for curve in curves:
        #flattenedCurves.append(shockFilter(curve,counter,workingDir,test))
    flattenedCurves = pool.map(shockFilter,curves)
    return flattenedCurves

def closing(image,kernelSize): 
    """
    Function to execute the closing operator. (dilate + erode)
    @type image: ArrayList
    @param image: Image, which has to be filtered
    @type kernelSize: Integer
    @param kernelSize: Size of the kernel, which should be used for dilation and erotion
    @rtype: 
        ArrayList
    @return: 
        Image, which had to be filtered
    """
    return ndimage.grey_closing(np.array(image), size=(kernelSize,kernelSize))

def gaussian(image, sigmaVal): 
    """
    Function to execute the gaussian filter.
    @type image: ArrayList
    @param image: Image, which has to be filtered
    @type sigmaVal: Integer
    @param sigmaVal: Sigma value to determine the kernel of the gaussian filter
    @rtype: 
        ArrayList
    @return: 
        Image, which had to be filtered
    """
    return ndimage.gaussian_filter(image, sigma=sigmaVal)

def logTransform(image): 
    """
    Function for the logarithmic transformation of the intensity values.
    @type image: ArrayList
    @param image: Image, which has to be transformed    
    @rtype: 
        ArrayList
    @return: 
        Image, which had to be transformed
    """
    val = 0
    image = np.array(image,float)
    for y in range(0,image.shape[0],1): 
        for x in range(0,image.shape[1],1):
            val = float(np.log2(float(image[y,x])+1.0))
            image[y,x] = val
    return image

def shift(image): 
    """
    Function to shift the logarithmized intensity values.
    @type image: ArrayList
    @param image: Image, which has to be transformed
    @rtype: 
        ArrayList
    @return: 
        Image, which had to be transformed
    """
    minVal = image.min()
    maxVal = image.max()
    for y in range(0,image.shape[0],1): 
        for x in range(0,image.shape[1],1):
            image[y,x] = int(((image[y,x] - minVal)/(maxVal-minVal))*255)
    return image

def edgeDetection(xPlot,yPlot,row, difThreshold,whiteThreshold,roi,lowerBoundary,upperBoundary): 
    """
    Function to detect possible boundary points of germinal centers.
    @type xPlot: ArrayList
    @param xPlot: List of mean intensity values in x direction
    @type yPlot: ArrayList
    @param yPlot: List of mean intensity values in y direction
    @type row: Integer
    @param row: Height of the row, about which we had calculated the mean values
    @type difThreshold: Float
    @param difThreshold: Threshold for a significant "jump"
    @param lowerBoundary: Smallest width or height of a germinal center in pixel
    @type lowerBoundary: Integer
    @param upperBoundary: Biggest width or height of a germinal center in pixel
    @type upperBoundary: Integer
    @param whiteThreshold: Minimum intensity inside a germinal center
    @type whiteThreshold: Integer
    @rtype: 
        ArrayList
    @return: 
        List of possible boundary points
    """
    possibleEdges = [[],[]]
    k = 0
    gap = 0
    for i in range(len(xPlot)): 
        k = 0
        while(k < len(xPlot[i])-1):
            curCoords = (int(max(i*row/2+5,0)),int(k))
            if(roi[curCoords]!=0):
                gap = 0
                if(xPlot[i][k+1]-xPlot[i][k]>difThreshold):
                    observer = True
                    save = k
                    k+=1
                    while(np.abs(xPlot[i][k]-xPlot[i][k+1])<difThreshold and k < len(xPlot[i])-2):
                        curCoords = (int(max(i*row/2+5,0)),int(k))
                        if(xPlot[i][k] > whiteThreshold and xPlot[i][k+1]> whiteThreshold and roi[curCoords]!=0):
                            k += 1
                            gap += 1
                        else:
                            k+=1
                            observer = False
                            gap += 1
                    if(gap > lowerBoundary and gap < upperBoundary and observer == True): 
                        possibleEdges[0].append((max(i*row/2+5,0),save))
                        possibleEdges[0].append((max(i*row/2+5,0),k))
                else: 
                    k += 1
            else:
                k+=1
    for i in range(len(yPlot)): 
        k = 0
        while(k < len(yPlot[i])-1):
            if(roi[k,(max(i*row//2+5,0))]!=0):
                gap = 0
                if(yPlot[i][k+1]-yPlot[i][k]>difThreshold):
                    observer = True
                    save = k
                    k+=1
                    while(np.abs(yPlot[i][k]-yPlot[i][k+1])<difThreshold and (k < len(yPlot[i])-2)):
                        curCoords = (int(k),int(max(i*row/2+5,0)))
                        if((yPlot[i][k] > whiteThreshold and yPlot[i][k+1]> whiteThreshold) and roi[curCoords]!=0):
                            k += 1
                            gap += 1
                        else:
                            k+= 1
                            observer = False
                            gap += 1
                    if(gap > lowerBoundary and gap < upperBoundary and observer == True): 
                        possibleEdges[1].append((save,(max(i*row/2+5,0))))
                        possibleEdges[1].append((k,(max(i*row/2+5,0))))
                else: 
                    k += 1
            else:
                k+=1
    return possibleEdges
            
def getConvexHull(edges,formFactorThreshold,eccentricityThreshold,areaMin,areaMax): 
    """
    Function to calculate convex hulls for a number of list of points
    @type edges: ArrayList
    @param edges: List of list of possible boundary points
    @rtype: 
        ArrayList
    @return: 
        Minimal list of possible boundary points
    """
    minSet = []
    centerOfMasses = {}
    edges = mlO.convertPoints(edges)
    it = 0
    object_id = 0
    for i in edges: 
        if(len(i)>4): 
            hull = ConvexHull(i)
            cy = np.mean(hull.points[hull.vertices,0])
            cx = np.mean(hull.points[hull.vertices,1])
            formFactor = (4*math.pi*hull.volume)/(hull.area**2)
            eccentricity = mlO.getEccentricity(hull.points,hull.volume)
            if(formFactor >= formFactorThreshold and hull.volume < areaMax and hull.volume > areaMin and eccentricity <= eccentricityThreshold):                
                qhull = mlO.collectAndReconvert(hull,edges,it)
                minSet.append(qhull)
                follicle = {}
                follicle["x"] = cx
                follicle["y"] = cy
                centerOfMasses[object_id]=follicle
                object_id = object_id + 1
        it += 1
    return minSet, centerOfMasses

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
    
def createMask(image,edges,workingDir): 
    """
    Function to mark white convex hulls, representing possible germinal centers 
    on a black image and saving it.
    @type image: ArrayList
    @param image: Template for the creation of a black copy
    @type workingDir: String
    @param workingDir: Path to the current working directory
    @type sep: String
    @param sep: Seperator to build up systempaths
    @type edges: ArrayList
    @param edges: Minimal list of possible boundary points
    """
    mask = createDefault(image)
    misc.imsave(workingDir+"without.tif",image) 
    for hull in edges: 
        mahotas.polygon.fill_polygon(hull,image)
        mahotas.polygon.fill_polygon(hull,mask)
    misc.imsave(workingDir+"marked.tif",image)
    return mask

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

def pointsForThreshold(xPlot,yPlot): 
    """
    Function to collect every intensity distances, later called "jump", between adjacent
    points. (0 excluded)
    @type xPlot: ArrayList
    @param xPlot: List of mean intensity values in x direction
    @type yPlot: ArrayList
    @param yPlot: List of mean intensity values in y direction
    @rtype: ArrayList
    @return: List of "jumps" greater then 0
    """
    k = 0
    points = []
    for i in range(len(xPlot)):
        k = 0
        while(k < len(xPlot[i])-1):
            jump = math.fabs(xPlot[i][k+1]-xPlot[i][k])
            if(jump>2):                    
                points.append(jump)
            k += 1
    for i in range(len(yPlot)): 
        k = 0
        while(k < len(yPlot[i])-1): 
            jump = math.fabs(yPlot[i][k+1]-yPlot[i][k])
            if(jump>2):                    
                points.append(jump)
            k += 1
    return points