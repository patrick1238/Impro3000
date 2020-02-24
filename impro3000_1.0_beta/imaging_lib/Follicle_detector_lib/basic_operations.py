import numpy as np
from Follicle_detector_lib import image_operations as iO
import scipy

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
    image = np.array(iO.gaussian(image,sigmaVal))
    image = np.array(iO.logTransform(image))
    image = np.array(iO.shift(image))
    image = iO.closing(image,kernelSize)
    return image
    
def markEdges(image,array,workingDir,call):
    """
    Function to mark given points inside an image.
    The image will be saved in the given working directory.
    @type workingDir: String
    @param workingDir:Path to the current working directory
    @type image: ArrayList
    @param image: Image, in which we want to mark point
    @type array: ArrayList
    @param array: ArrayList, with the points we want to highlight
    @type sep: String
    @param sep: Seperator to build up systempaths
    @type call: String
    @param call: String, to discriminate between different marked images
    """
    for x in array:
        for i in x:
            image[int(i[0]),int(i[1])] = 0
    scipy.misc.toimage(image, cmin=0, cmax=255).save(workingDir+str(call)+"marked.tif")
    
    
    
    
    
    
    
        