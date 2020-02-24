"""
Module to save communities mapped on to img for visualisation 

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



def save_as_image(communities, img, out_path, grayscale):
	""" maps communities to image and saves the image to disk """
	color=iter(plt.cm.rainbow(np.linspace(0,1,len(communities))))
	# each community gets it's own layer on the plot
	for com_index in range(len(communities)):
		c=next(color) # color for community visulaization

		graph = communities[com_index]
		py_dot_graph = nx.drawing.nx_pydot.to_pydot(graph)                 

		#building pos_dict:
		node_dict_tmp = nx.get_node_attributes(graph, "position") # for item in .. item: node_1
		vertex_dictionary = collections.OrderedDict(sorted(node_dict_tmp.items()))

		pos = {}
		# rescale graph to layer 3:
		import scale_graph as sg
		for vertex in vertex_dictionary:
			tmp_positions = vertex_dictionary.get(vertex)
			tmp_positions = list(tmp_positions)
			scaled_tmp_positions = sg.downscale_positions(tmp_positions, 3)
			pos[vertex] = scaled_tmp_positions
		if grayscale:
			plt.imshow(img, "gray", zorder=0, alpha=0.3)
		else:
			plt.imshow(img, zorder=0, alpha=0.3)
		nx.draw_networkx(graph, zorder=com_index+1, pos=pos, node_size=0.05, node_color=c, alpha=0.7, width=0.05,  with_labels=False, label="com_" + str(com_index))	
	
	plt.grid("on")
	print("[view_and_save_communities] plotting succefull, saving to disk now - this takes a while, nothing is broken")
	plt.savefig(out_path, dpi=1000)
	plt.clf() 

	

def main(arguments, communities_list, img_path, graph_layout, k_value, grayscale, name):
	print("[view_and_save_communities] creating image")
	img = imread(img_path)
	out_path = arguments["mapped_images_dir"] + arguments["img_name"] + "_" + name + "_k_" + str(k_value) + "_mapped_" + graph_layout + ".tif"
	save_as_image(communities_list, img, out_path, grayscale)
	print("[view_and_save_communities] done")





