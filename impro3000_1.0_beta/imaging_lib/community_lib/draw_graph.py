"""
Module to save gml-files viualized as imges to disk. 
expects that the gml graph originates from layer 0, rescales it's coordinates to layer 3 

@author: Henrik Gollek

"""


import networkx as nx
import ntpath
import os
import matplotlib.pyplot as plt
import graphviz  
import collections # ordering the dict
from scipy.misc import imread


# SCALING TO LAYER 3, keep in mind!
def read_and_print(graph, out_path, name):
	""" saves the input graph as .tif with matplotlib """
	py_dot_graph = nx.drawing.nx_pydot.to_pydot(graph)                 

	#building pos_dict:
	node_dict_tmp = nx.get_node_attributes(graph, "position") # for item in .. item: node_1
	vertex_dictionary = collections.OrderedDict(sorted(node_dict_tmp.items()))
	print("building postion dictionary")
	pos = {}
	# scaling to layer 3:
	import scale_graph as sg
	for vertex in vertex_dictionary:
		tmp_positions = vertex_dictionary.get(vertex)
		pos[vertex] = tmp_positions

	nx.draw_networkx(graph, zorder=0, pos=pos, node_size=0.05, node_color="blue", alpha=0.7, width=0.05,  with_labels=False)
	plt.grid("on")
	plt.savefig(out_path + name + ".tiff", dpi=1000)
	plt.clf() 


def main(graph, out_path, name):
	read_and_print(graph, out_path, name)


if __name__ == '__main__':
	main(graph, out_path, name)