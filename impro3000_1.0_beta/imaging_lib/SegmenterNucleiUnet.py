# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 15:00:16 2018

@author: alisa
"""
import segmenter_interface
import nuclei_segmentation_lib.segmentation_postprocessing as segmentation_postprocessing
import cv2
import numpy as np
import ImageObject
from nuclei_segmentation_lib.unet_nuclei import myUnet
from pathlib import Path
import os

class SegmenterNucleiUnet(segmenter_interface.Segmenter):
    def __init__(self, image_object, csvpath):
        #super().__init__()
        self.seg_image = image_object.get_numpy_array()
        #self.seg_image = cv2.imread("E:/Users/Hodgkin/Desktop/develop/branches/impro3000_1.0_beta/imaging_lib/nuclei_segmentation_lib/test.tif", 0)
        self.width = image_object.get_width()
        self.height = image_object.get_height()
        self.global_x = image_object.get_global_x()
        self.global_y = image_object.get_global_y()
        self.tile_id = image_object.get_id()
        self.csvpath = csvpath + self.tile_id+ "objects.csv"
        self.measurer = segmentation_postprocessing.Measurer(self.csvpath, self.global_x, self.global_y, self.tile_id, 30)


    def segment(self):
        #super().segment()
        """Segments nuclei via Unet
        """
        segmentation_set = self.create_segmentation_set()
        prediction_set = self.predict(segmentation_set)
        bin_img = self.merge_binary_image(prediction_set)
        #print(bin_img)
        cv2.imwrite(self.tile_id+"_bin_tmp.tif", bin_img)
        labels, mask = self.watershed(bin_img)
        os.remove(self.tile_id+"_bin_tmp.tif")
        #cv2.imwrite(self.tile_id+"_bin_mask.tif", mask)
        print("measure")
        self.measurer.measure_objects(mask, labels)
        print("write csv")
        self.measurer.write_measurements(self.csvpath)
        return bin_img

    def merge_binary_image(self, prediction_set):
        """Merges 512x512 pixel tiles
        
        Arguments:
            
        prediction set -- numpy array of predicted 512x512 pixel images 
        """
        new_height = self.height+512-self.height % 512
        new_width = self.width+512-self.width % 512
        
        merged_img = np.ndarray((new_height, new_width))

        i = 0
        for x in range(int(new_width/512)):
            x *= 512
            for y in range(int(new_height/512)):
                y *= 512

                merged_img[y:y+512, x:x+512] = np.reshape(prediction_set[i],(512,512))[0:512, 0:512]
                i+=1

        
        for x in range(new_width):
            for y in range(new_height):
                if (merged_img[x][y] >= 0.5):
                    merged_img[x][y] = 255
                else:
                    merged_img[x][y] = 0


        return merged_img[0:self.height, 0:self.width]



    def create_segmentation_set(self):
        """Crops image into 512x512 tiles for prediction
        """

        devidable_seg_image = self.make_devidable() 
        #print("netzinput:", devidable_seg_image[0], devidable_seg_image[-1])
        stepsx = int(len(devidable_seg_image[0])/512)
        stepsy = int(len(devidable_seg_image)/512)
        imgdatas = np.ndarray((stepsx*stepsy,512,512,1), dtype=np.uint8)
        i = 0

        for x in range(stepsx):
            x = x*512
            for y in range(stepsy):
                y = y*512
                imgdatas[i] = np.reshape((devidable_seg_image[y:(y+512), x:(x+512)]),(512,512,1))

                i += 1
                #print("i", i)
        return imgdatas
    


    def make_devidable(self):
        """Adds black pixels so that image is devidable by 512
        """

        rest_x = self.width % 512
        rest_y = self.height % 512
        #print(self.width, "= realwidth", self.height, "=realheight")
        #print(rest_x, "= rest_x ", rest_y, "= rest_y")

        devidable_seg_image = np.ndarray((self.height+512-rest_y, self.width+512-rest_x))
        devidable_seg_image[0:self.height, 0:self.width] = self.seg_image

        return devidable_seg_image




    def predict(self,segmentation_set): 
        """Starts prediction
        
        Arguments:
            
        segmentation_set -- numpy ndarray of 512x512 pixel images to segment
        """
        segmentation_set = segmentation_set.astype('float32')
        segmentation_set /= 255

        myunet = myUnet()
        model = myunet.get_unet()
        weights = Path('../imaging_lib/nuclei_segmentation_lib/unet2test.hdf5')
        #print(weights)
        #print(weights.absolute())
        model.load_weights(weights.absolute())
        imgs_mask_test = model.predict(segmentation_set, verbose=1)
        return imgs_mask_test

    def watershed(self,img):
        img = cv2.imread(self.tile_id+"_bin_tmp.tif")
        #print("image before ws:", img)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        for x in range(512):
            for y in range(512):
                if gray[x][y] < 127:
                    gray[x][y] = 0
                else:
                    gray[x][y] = 255
                    


        #print(np.unique(gray))
        thresh = gray
                
        #ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        kernel = np.ones((3,3),np.uint8)
        opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
        sure_bg = cv2.dilate(opening,kernel,iterations=3)
        dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,0)
        ret, sure_fg = cv2.threshold(dist_transform,0.15*dist_transform.max(),255,3)
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg,sure_fg)
        ret, markers = cv2.connectedComponents(sure_fg)
        markers = markers+1
        markers[unknown==255] = 0
        labels_ws = cv2.watershed(img,markers)
        #img[markers == -1] = [255,0,0]
        labels_ws[labels_ws == -1] = 0
        labels_ws[labels_ws == 1] = 0  
        
        
        return len(np.unique(labels_ws))-1, labels_ws



'''

###TEST###

test_img = cv2.imread("test.png", 0)
io = ImageObject.ImageObject(numpy_array = test_img, width = 512, height = 512, x_coord = 10, y_coord = 50, objectID = 3)
print("width", len(test_img))
test = SegmenterNucleiUnet(io, "/")

cv2.imwrite("outtest.jpg", test.segment())'''
