"""
Module to correlate eosinophilic regiosn with communities.
- calculates convex hull around communities
- expands the convex hull by a fixed value 
- checks who much eosinophilic tissue is inside this "ring" region 

@author: Henrik Gollek

"""

import networkx as nx
import ntpath
import os
import matplotlib.pyplot as plt
import graphviz  
import collections # ordering the dict
from scipy.misc import imread
import numpy as np
import scipy
import math
from PIL import Image, ImageDraw
import csv
sys.path.append("..")
from imaging import WSI
from imaging import roi_detector


expansion_value = 100 # distance between convex hull and outer ring in pixels -> area in where cellfree percentage is determined


def generate_coordinates_array(community): 
	""" get all coordinates from the cellgraph and rescale tehm to layer 3.
	returns list with rescaled coordinates. """
	node_dict_tmp = nx.get_node_attributes(community, "position") 
	vertex_dictionary = collections.OrderedDict(sorted(node_dict_tmp.items()))
	coord_array = []
	# scaling factor layer 0 to layer 3:
	scaling_factor = 1/32
	for vertex in vertex_dictionary:
		tmp_positions = vertex_dictionary.get(vertex)
		tmp_positions = list(tmp_positions)	
		# rescales position values
		for list_index in range(len(tmp_positions)):
			tmp_positions[list_index] = int(tmp_positions[list_index] * scaling_factor)	
		# list with lists of rescaled positions (x,y coordinates)
		coord_array.append(tmp_positions)
	return coord_array 

def get_convex_hull(coord_array):
	""" returns the convex hull of the input vertex's coordiantes. output format is not straight forward. """
	convex_hull = scipy.spatial.ConvexHull(coord_array)
	return convex_hull


def get_hull_vertices(convex_hull):
	""" retuens the vertices of the convex hull as coordinates tuples. """
	hull_vertices = convex_hull.points[convex_hull.vertices]
	return hull_vertices


def get_perpendicular_foot(vertex1, vertex2, point):
	""" function to calculate perpendicular foor to 2 vertices.
		resturns x and y value of the foot. """
	x1 = int(vertex1[0])
	y1 = int(vertex1[1])
	x2 = int(vertex2[0])
	y2 = int(vertex2[1])
	x3 = int(point[0])
	y3 = int(point[1])
	# get the foot:
	k = (((y2-y1) * (x3-x1) - (x2-x1) * (y3-y1))) / (((y2-y1)**2 + (x2-x1)**2))
	x4 = x3 - k * (y2-y1)
	y4 = y3 + k * (x2-x1)

	perpendicular_foot = [x4, y4]
	return perpendicular_foot


def get_outer_hull_point(point, perpendicular_foot, expansion):
	""" get the point's coordiantes in the defined distance (expansion) from convex hull. 
		point will be outside the convex hull's area.  """
	x1 = point[0]
	y1 = point[1]
	x2 = perpendicular_foot[0]
	y2 = perpendicular_foot[1]

	vector = (x2-x1, y2-y1)
	vector_abs = math.sqrt((x2-x1)**2 + (y2-y1)**2)
	vector_normalized = [vector[0]/vector_abs, vector[1]/vector_abs]

	new_point = [int(x1 - vector_normalized[0]*expansion), int(y1 - vector_normalized[1]*expansion)]
	return new_point

	

def get_outer_hull(hull_vertices):
	""" returns all vertex coordinates to the expanded convex hull. """
	outer_hull_tmp = []
	for i in range(len(hull_vertices)):
		# if, elif: accounting for the two vertices, that otherwise wouldn't be iterated over
		if i == len(hull_vertices)-2:
			vertex1 = hull_vertices[i]
			vertex2 = hull_vertices[0]
			point = hull_vertices[i+1]
		elif i == len(hull_vertices)-1:
			vertex1 = hull_vertices[i]
			vertex2 = hull_vertices[1]
			point = hull_vertices[0]
		else:
			vertex1 = hull_vertices[i]
			vertex2 = hull_vertices[i+2]
			point = hull_vertices[i+1]

		perpendicular_foot = get_perpendicular_foot(vertex1, vertex2, point)
		outer_hull_point = get_outer_hull_point(point, perpendicular_foot, expansion_value)
		outer_hull_tmp.append(outer_hull_point)
	
	outer_hull = np.array(outer_hull_tmp)
	return outer_hull
	

def provide_mask(vertices, arguments, roi_numpy):
	""" returns a masked numpy array. the mask is based on the input coordinates:
		1. create poygon from coordinates
		2. translate polygon into an ndarray
		3. use said ndarray as mask """
	polygon = list(map(tuple, vertices))
	img = Image.fromarray(roi_numpy)
	ImageDraw.Draw(img).polygon(polygon, outline=0, fill=0)
	mask = np.array(img) 
	mask.astype("uint8")
	mask[mask == 0] = False
	mask[mask == 255] = True
	return mask


def create_numpy_mask(cell_free_binary_numpy, inner_mask, outer_mask):
	""" returns a masked ndarray: only the region defined between the convex hull and the expanded convex hull is accasible. """
	inner_mask_reverse = np.logical_not(inner_mask)
	binary_with_inner_mask = np.ma.masked_array(cell_free_binary_numpy, inner_mask_reverse)
	binary_with_both_masks = np.ma.masked_array(binary_with_inner_mask, outer_mask)
	return binary_with_both_masks


def get_cell_free_binary_numpy(arguments):
	""" load binary image of eosinophilic regions and return as ndarray """
	cell_free_numpy = np.array(Image.open(arguments["results"]+"cell_free_binary.tif"))
	return cell_free_numpy


def get_cellfree_percentage(cell_free_binary_numpy, inner_mask, outer_mask, arguments, cell_free_binary_numpy_masked):
	""" return percentage of eosinophilic region within the unmasked area around community. """
	pixel_total = 0
	pixel_cell_free = 0
	for y in range(0,cell_free_binary_numpy_masked.shape[0],1):
		for x in range(0, cell_free_binary_numpy_masked.shape[1], 1):
			if inner_mask[y,x] and not outer_mask[y,x]:
				pixel_total += 1
				#print(cell_free_binary_numpy_masked[y,x])
				if not cell_free_binary_numpy_masked[y,x]: # != 0:
					pixel_cell_free += 1

	if pixel_cell_free > 0:
		percent = int((pixel_cell_free/pixel_total)*100)
	else:
		percent = 0
	return percent







###################################################### MAIN ###################################################



def analyze_communities(community_dict, binary_cellfree, arguments):
	""" performs all neccessary steps to correlate commmunitys with eosinophilic tissue.  """
	percentage_list = []
	
	analyze_dict = {}


	for key, value in community_dict:
		community = value
		coord_array = generate_coordinates_array(community)
		convex_hull = get_convex_hull(coord_array)
		hull_vertices = get_hull_vertices(convex_hull)
		outer_hull = get_outer_hull(hull_vertices)
		cell_free_binary_numpy = binary_cellfree
		# get roi for masking:
		wsi_object = WSI.WSI(arguments["input_path"])
		layer_3 = wsi_object.get_RGB_numpy_array(layer=3)
		roi_numpy = roi_detector.detect_roi(layer_3)
		# create the masks to only consider the area sourounding the community:
		inner_mask = provide_mask(hull_vertices, arguments)
		outer_mask = provide_mask(outer_hull, arguments)
		cell_free_binary_numpy_masked = create_numpy_mask(cell_free_binary_numpy, inner_mask, outer_mask)
		# get the percentage of cellfree tissue around community:
		com_percentage = get_cellfree_percentage(cell_free_binary_numpy, inner_mask, outer_mask, arguments, cell_free_binary_numpy_masked)
		
		# initiate further dict for each community to store all future analyzing results:
		analyze_dict[key] = {}
		# fill said sub-dict with the cellfree percentage value
		analyze_dict[key]["cellfree_percentage"] = com_percentage

		

	
	
	
	

		

