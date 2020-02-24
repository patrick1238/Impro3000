# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 12:01:06 2018

@author: Hodgkin
"""

import scipy.ndimage as ndi
import numpy as np
import pandas as pd
import cv2


class Measurer:
    
    CSV_FORMAT = '.csv'
    ident = 'ID'
    coords = 'Coordinates'
    size_id = 'Size'
    circ_id = 'Circumference'
    #contour_id = 'Contour_Profile'
    eigen_id = 'Eigenvectors'
    edt_id = 'EDT_Descriptor'
    roundness_id = 'Roundness'
    column_names = [ident, coords, size_id, circ_id, eigen_id, roundness_id]
    micrometers_to_pixels = 0.125
    contour_profile_length = 100
    
    
    def __init__(self, path, global_x, global_y, tile_id, filter_size=150):
        self.object_sizes = []
        self.coordinates = []
        self.circumferences = []
        #self.contour_profiles = []
        self.eigen_vectors = []
        self.edt_descriptors = []
        self.roundnesses = []
        self.object_index = 0
        self.size_filter = filter_size
        
        self.path = path
        self.global_x = global_x
        self.global_y = global_y
        self.tile_id = tile_id
        self.center_x = []
        self.center_y = []
        
    def measure_single_object(self, mask):
        size = np.sum(mask)
        transformed = ndi.morphology.distance_transform_edt(mask)
        circumference = np.sum(transformed == 1)
        roundness =  4 * np.pi * size / (circumference**2)
        eigen = self.get_largest_eigen(mask)
        return size, circumference, roundness, eigen
    
    def measure_objects(self, segmented, num_labels=0):
        if (num_labels == 0):
            labeled, num_features = ndi.measurements.label(segmented)
        else:
            labeled = segmented
            num_features = num_labels
        object_ids = range(1, num_features+1)
        print('found {} objects'.format(num_features))
        centers = ndi.measurements.center_of_mass(segmented, labeled, object_ids)
        #print("calculated center of mass")
        border_labels = self.get_border_object_labels(labeled)
        #print("border labels", border_labels)
        #print("calculated border labels")
        for i in object_ids:
            #print("id", i)
            #if (i in border_labels):
            #    pass
            obj = (labeled == i)
            size = np.sum(obj)
            
            transformed = ndi.morphology.distance_transform_edt(obj)
            circumference = np.sum(transformed == 1)
            #print("calculated circumference")
                #edt_descriptor = self.compute_edt_descriptor(transformed, size)
                #eigen = self.get_largest_eigen(obj)
            roundness =  4 * np.pi * size / (circumference**2)
            #print("eigen und round")
            if size > 10 and size < 1000:
                self.roundnesses.append(roundness)
                self.object_sizes.append(size)
                self.coordinates.append(centers[i-1])
                self.circumferences.append(circumference)
                #self.edt_descriptors.append(edt_descriptor)
                #self.eigen_vectors.append(eigen)
                self.object_index += 1
        print('Measured {} objects after filtering'.format(self.object_index))
    
    def raw_moment(self, data, i_order, j_order):
      nrows, ncols = data.shape
      y_indices, x_indicies = np.mgrid[:nrows, :ncols]
      return (data * x_indicies**i_order * y_indices**j_order).sum()
    
    def get_border_object_labels(self, labeled):
        lower = np.unique(labeled[labeled.shape[0]-1,:])
        if (0 in lower):
            lower = lower[1:]
        upper = np.unique(labeled[0,:])
        if (0 in upper):
            upper = upper[1:]
        left = np.unique(labeled[:,0])
        if (0 in left):
            left = left[1:]
        right = np.unique(labeled[:,labeled.shape[1]-1])
        if (0 in right):
            right = right[1:]
        whole = np.concatenate((lower, upper, left, right))
        return whole
    
    
    def moments_cov(self, data):
      data_sum = data.sum()
      m10 = self.raw_moment(data, 1, 0)
      m01 = self.raw_moment(data, 0, 1)
      x_centroid = m10 / data_sum
      y_centroid = m01 / data_sum
      u11 = (self.raw_moment(data, 1, 1) - x_centroid * m01) / data_sum
      u20 = (self.raw_moment(data, 2, 0) - x_centroid * m10) / data_sum
      u02 = (self.raw_moment(data, 0, 2) - y_centroid * m01) / data_sum
      cov = np.array([[u20, u11], [u11, u02]])
      return cov
    
    def get_largest_eigen(self, im):
        cov = self.moments_cov(im)
        evals, evecs = np.linalg.eig(cov)
        sort_indices = np.argsort(evals)[::-1]
        x_v1, y_v1 = evecs[:, sort_indices[0]]  # Eigenvector with largest eigenvalue
        return x_v1, y_v1

    
    def get_single_contour_profile(self, im):
        filled = ndi.morphology.binary_fill_holes(im).astype(int)
        center = ndi.measurements.center_of_mass(filled)
        dst_transform = ndi.distance_transform_edt(filled)
        y_coords, x_coords =  np.where(dst_transform == 1)
        profile_vectors = self.get_sorted_coords(center,y_coords, x_coords)
        profile = self.compute_distances(center, profile_vectors)
        profile = self.normalize_profile_length(profile)
        return profile
        
    def length(self, coord):
            return np.sqrt(coord[0]**2+coord[1]**2)
    
    def get_min_vec(self, coords, get_index=True):
            lengths =  np.apply_along_axis(self.length, 0, coords)
            index = np.argmin(lengths)
            if get_index:
                return index
            else:
                return coords[:,index]
    
    def compute_distances(self, coord, coord_list):
        distances = []
        for i in range(len(coord_list)):
            dist = np.sqrt((coord_list[i][0] - coord[0])**2 + (coord_list[i][1] - coord[1])**2)
            distances.append(dist)
        return distances
        
    def get_sorted_coords(self, com, y_coords, x_coords):
        distances = []
        sorted_coords = []
        coords = np.array((np.copy(y_coords), np.copy(x_coords)))
        for i in range(len(x_coords)):
            dist = np.sqrt((y_coords[i] - com[0])**2 + (x_coords[i] - com[1])**2)
            distances.append(dist)
        maxdist_index = np.argmax(distances)
        sorted_coords.append(coords[:,maxdist_index])
        np.delete(distances, maxdist_index)
        coords = np.delete(coords, maxdist_index, axis=1)
        current_vector = sorted_coords[0]
        for i in range(len(distances)-1):
            temp = coords-current_vector[:,np.newaxis]
            next_index = self.get_min_vec(temp)
            current_vector = coords[:,next_index]
            sorted_coords.append(current_vector)
            coords = np.delete(coords, next_index, axis=1)
        return sorted_coords
    
    def normalize_profile_length(self, profile, length=100):
        factor = float(len(profile)) / float(length-1)
        out = []
        orig_step = 0.
        num_medians = 0
        index = 0
        rest = 0
        for i in range(len(profile)):
            if (index == len(profile) or orig_step >= len(profile)):
                break
            if (((orig_step - index) > 1) and (orig_step - index > 0)):
                if (rest > 1):
                    orig_step += 1
                    rest -= 1
                out.append(np.median(profile[index:int(orig_step)+1]))
                num_medians += 1
                index = int(orig_step)
                rest += orig_step - float(index)
                orig_step = index
            else:
                out.append(profile[index])
            orig_step += factor
            index += 1
        return out
    
    def get_contour_profiles(self, im):
        filled = ndi.morphology.binary_fill_holes(im).astype(int)
        labeled_array, num_features = ndi.measurements.label(filled)
        centers = ndi.measurements.center_of_mass(filled, labeled_array, range(1,num_features+1))
        dst_transform = ndi.distance_transform_edt(filled)
        profiles = []
        for i in range(1,num_features+1):
            condition = labeled_array == i
            dst_transform_values = np.extract(dst_transform, condition)
            profile_vectors = self.get_sorted_coords(centers[i-1], np.where(dst_transform_values == 1))
            profiles.append(self.compute_distances(centers[i-1], profile_vectors, norm_dim=True))
        return profiles
            
    def write_measurements(self, path):
        #make id "tile_id"
        ids = []
        ratios = []
        for x in range(0, self.object_index):
            ids.append(str(self.tile_id)+"."+str(x))
            ratios.append(float(self.circumferences[x])/self.object_sizes[x])
            
        #split coordinates
        for coord in self.coordinates:
            self.center_x.append(coord[0])
            self.center_y.append(coord[1])
            
        print("Länge", len(ids), len(self.center_x))
        table_dict = {'ID' : ids[1:], 'Center_x' : self.center_x[1:], 'Center_y' : self.center_y[1:], 'Size' : self.object_sizes[1:], 'Circumferences' : self.circumferences[1:],  'Roundnesses' : self.roundnesses[1:], 'Ratios' : ratios[1:]}
        table = pd.DataFrame.from_dict(table_dict)
        print(table)
        if (self.CSV_FORMAT in path):
            table.to_csv(path)          
        else:
            print("CAN ONLY WRITE CSV FORMAT. THE FILE NEEDS TO END WITH .csv! ABORTING!")
            return
        
    def read_measurements(self, path):
        table = pd.read_csv(path)
        self.object_sizes = table['Size'].tolist()
        self.coordinates = table['Coordinates'].tolist()
        self.object_index = self.object_index + len(self.coordinates)
        
    def get_filtered_data(self, column_id, filter_function):
        if (column_id in self.column_names):
            out = []
            ids = []
            targets = []
            if (column_id == self.size_id):
                targets = self.sizes
            elif (column_id == self.coords):
                targets = self.coordinates
            elif (column_id == self.circ_id):
                targets = self.circumferences
            for ID, target in zip(range(1, self.object_index +1), targets):
                if (filter_function(target)):
                    ids.append(ID)
                    out.append(target)
        return ids, out

    def get_sizes_in_micrometers(self):
        out = self.sizes * self.micrometers_to_pixels
        return out
    
    def compute_edt_descriptor(self, transformed, size):
        edt_values = np.array([1, np.sqrt(2), 2, np.sqrt(5), 3, np.sqrt(10)]) # values to counted for descriptor
        out = np.zeros(6)
        unique, counts = np.unique(transformed, return_counts=True)
        unique = unique[1:] # ignore zeros
        counts = counts[1:]
        indices_unique = [np.where(unique == i)[0][0] for i in edt_values if (np.where(unique == i)[0].size == 1)] # find occurences of edt values in unique
        indices_edt = [np.where(edt_values == i)[0][0] for i in unique if (np.where(edt_values == i)[0].size == 1)] # find occurences of unique in edt values
        for i in range(len(indices_unique)): # file out with counts
            u_index = indices_unique[i] # where the count is
            edt_index = indices_edt[i] # where the count should be written to
            out[edt_index] += counts[u_index]
        norm_counts = out / size # normalze
        return norm_counts
    
    
def watershed(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #print(gray)
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
    #print(ret, "ANZAHL")
    markers = markers+1
    markers[unknown==255] = 0
    labels_ws = cv2.watershed(img,markers)
    #img[markers == -1] = [255,0,0]
    labels_ws[labels_ws == -1] = 0
    labels_ws[labels_ws == 1] = 0
    #print(labels_ws[0])
    #print(labels_ws[1])
    #print(np.unique(labels_ws))   
    
    
    return len(np.unique(labels_ws))-1, labels_ws
    
    """
m = Measurer(30)
#mask = cv2.imread("unet-master/results/t1270.tif")

#mask = cv2.imread("evaluation/11/3_ws.tif",)
mask = cv2.imread("/home/alisa/Masterarbeit/benchmark/results/bin_stomach.tif")

num_label, mask = watershed(mask)

#print(mask
#m.measure_objects(mask, num_label)
m.measure_objects(mask, num_label)
#m.write_measurements("unet-master/results/t1270.csv")

#m.write_measurements("evaluation/11/3_ws.csv")
m.write_measurements("/home/alisa/Masterarbeit/benchmark/results/bin_stomach.csv")

for x in range(1000):
    for y in range(1000):
        if mask[x][y] > 0:
            mask[x][y] = 255
        
cv2.imwrite("/home/alisa/Masterarbeit/benchmark/results/ws_stomach2.tif", mask)
#print(m.coordinates
testim = np.zeros([1000,1000])
for c in m.coordinates:
    marker_shape=(9,9)
    border = marker_shape[0]/2
    x, y = int(c[0]),int(c[1])
    #print(x, y
    cv2.circle(testim,(y,x), 5, 255)
    
#cv2.imwrite("evaluation/11/3_ws_pos.png", testim)
cv2.imwrite("/home/alisa/Masterarbeit/benchmark/results/test.jpg", testim)
print"das war das skript"""
