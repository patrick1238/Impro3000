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

# commmunities above threshhol dwill be saved to disk: 
percentage_threshhold = 45


def generate_coordinates_array(graph): 
	""" get all coordinates from the cellgraph and rescale tehm to layer 3.
	returns list with rescaled coordinates. """
	node_dict_tmp = nx.get_node_attributes(graph, "position") 
	vertex_dictionary = collections.OrderedDict(sorted(node_dict_tmp.items()))
	coord_array = []
	# rescaling to layer 3
	import scale_graph as sg
	for vertex in vertex_dictionary:
		tmp_positions = vertex_dictionary.get(vertex)
		tmp_positions = list(tmp_positions)
		scaled_tmp_positions = sg.downscale_positions(tmp_positions, 3)
		coord_array.append(scaled_tmp_positions)
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

	

def get_outer_hull(hull_vertices, expansion):
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
		outer_hull_point = get_outer_hull_point(point, perpendicular_foot, expansion)
		outer_hull_tmp.append(outer_hull_point)
	
	outer_hull = np.array(outer_hull_tmp)
	return outer_hull
	

def provide_mask(vertices, arguments):
	""" returns a masked numpy array. the mask is based on the input coordinates:
		1. create poygon from coordinates
		2. translate polygon into an ndarray
		3. use said ndarray as mask """
	polygon = list(map(tuple, vertices))
	img = Image.open(arguments["tmp"]+"ROI.tif")
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


def save_masked_numpy(outer_hull, hull_vertices, arguments, community, masked_numpy, expansion_value, counter, com_percentage):
	""" save input community with sourounding masjed area to disk. """
	a,b = outer_hull.T
	c,d = hull_vertices.T

	node_dict_tmp = nx.get_node_attributes(community, "position") # for item in .. item: node_1
	vertex_dictionary = collections.OrderedDict(sorted(node_dict_tmp.items()))
	pos = {}
	import scale_graph as sg
	for vertex in vertex_dictionary:
		tmp_positions = vertex_dictionary.get(vertex)
		tmp_positions = list(tmp_positions)
		scaled_tmp_positions = sg.downscale_positions(tmp_positions, 3)
		pos[vertex] = tmp_positions


	plt.imshow(masked_numpy, "gray")
	plt.scatter(a,b, s=2)
	nx.draw_networkx(community, zorder=0, pos=pos, node_size=0.05, node_color="blue", alpha=0.7, width=0.05,  with_labels=False)
	plt.scatter(c,d, s=2)
	#plt.savefig(arguments["cell_free_results_dir"] + "community_1_area_of_interest.tif", dpi=1000)
	plt.savefig(arguments["tmp"] + "community_" + str(counter) + "_eos_region_" + str(com_percentage) + "_percent.tif", dpi=1000)
	plt.clf()



def get_cell_free_binary_numpy(arguments):
	""" load binary image of eosinophilic regions and return as ndarray """
	cell_free_numpy = np.array(Image.open(arguments["results"]+"cell_free_binary.tif"))
	return cell_free_numpy


def get_cellfree_percentage(cell_free_binary_numpy, inner_mask, outer_mask, arguments, counter, cell_free_binary_numpy_masked):
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


def save_cellfree_information(arguments, percentage_list):
	""" save community number and percentage of eosinophilic tissue into csv to disk """
	with open(arguments["cell_free_results_dir"] + arguments["img_name"] + "_cell_free_results.csv", 'w', newline='') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		for i in range(len(percentage_list)):
			filewriter.writerow(["community_"+str(i), str(percentage_list[i])])



def plot_cell_free_percentage(arguments, percentage_list):
	""" plot the percentages of eosinophilic tissue around communities for all communities. """
	name = arguments["img_name"]
	np_percentage_list = np.asarray(percentage_list)
	unique_values, counts = np.unique(np_percentage_list, return_counts=True)
	plt.plot(unique_values, counts)
	print("values:", unique_values)
	print("counts:", counts)
	plt.ylabel('Anzahl Communitys', fontsize=18)
	plt.xlabel('Eosinophile Region [%]', fontsize=16)
	plt.savefig(arguments["cell_free_results_dir"] + name + "_cellfree_plot.tif", dpi=200)
	plt.clf()


	# boxplot:
	plt.boxplot(percentage_list)
	plt.savefig(arguments["cell_free_results_dir"] + name + "_cellfree_BOX_plot.tif", dpi=200)
	plt.clf()



def main(arguments, communities_list, expansion_value):
	""" performs all neccessary steps to correlate commmunitys with eosinophilic tissue.  """
	percentage_list = []
	counter = 0
	for community in communities_list:
		counter += 1
		coord_array = generate_coordinates_array(community)
		convex_hull = get_convex_hull(coord_array)
		hull_vertices = get_hull_vertices(convex_hull)
		outer_hull = get_outer_hull(hull_vertices, expansion_value)
		cell_free_binary_numpy = get_cell_free_binary_numpy(arguments)
		inner_mask = provide_mask(hull_vertices, arguments)
		outer_mask = provide_mask(outer_hull, arguments)

		cell_free_binary_numpy_masked = create_numpy_mask(cell_free_binary_numpy, inner_mask, outer_mask)


		com_percentage = get_cellfree_percentage(cell_free_binary_numpy, inner_mask, outer_mask, arguments, counter, cell_free_binary_numpy_masked)
		percentage_list.append(com_percentage)

		# save all communities with com_percentage above threshold:
		if com_percentage >= percentage_threshhold:
			save_masked_numpy(outer_hull, hull_vertices, arguments, community, cell_free_binary_numpy_masked, expansion_value, counter, com_percentage)


	save_cellfree_information(arguments, percentage_list)
	plot_cell_free_percentage(arguments, percentage_list)
	
	

		

