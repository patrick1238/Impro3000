"""
Module to rescale coordiantes in the ranges of layer 0 to 3

@author: Henrik Gollek

"""

import networkx as nx
import collections # ordering the dict



def set_scaling_factor(layer, do_upscale):
	# upscaling from layer 3
	if do_upscale:
		if layer == 0: # from layer 3 to 0
			scaling_factor = 32
		elif layer == 1: # from layer 3 to 1
			scaling_factor = 16
		elif layer == 2: # from layer 3 to 2
			scaling_factor = 4
	# downscaling from layer 0
	else:
		if layer == 1: # layer 0 to 1
			scaling_factor = 1/4
		elif layer == 2: # layer 0 to 2
			scaling_factor = 1/16
		elif layer == 3: # layer 0 to 3
			scaling_factor = 1/32
	return scaling_factor



def build_position_dictionary(graph, scaling_factor):
	node_dict_tmp = nx.get_node_attributes(graph, "position") # for item in .. item: node_1
	vertex_dictionary = collections.OrderedDict(sorted(node_dict_tmp.items()))

	scaled_positions = {}

	for vertex in vertex_dictionary:
		tmp_positions = vertex_dictionary.get(vertex)
		tmp_scaled_positions = []
		for list_index in range(len(tmp_positions)):
			tmp_scaled_positions.append(int(tmp_positions[list_index] * scaling_factor))
		scaled_positions[vertex] = tmp_scaled_positions

	nx.set_node_attributes(graph, scaled_positions, "position")

	node_dict_tmp = nx.get_node_attributes(graph, "position") # for item in .. item: node_1
	vertex_dictionary = collections.OrderedDict(sorted(node_dict_tmp.items()))

	for vertex in vertex_dictionary:
		tmp_positions = vertex_dictionary.get(vertex)
	return graph


def scale_positions(positions, scaling_factor):
	for list_index in range(len(positions)):
		positions[list_index] = int(positions[list_index] * scaling_factor)
	return positions


def rescale_position_dictionary(position_dirctionary, layer):
	return rescaled_position_dictionary


def build_rescaled_graph(rescaled_position_dictionary):
	return rescaled_graph


def upscale_graph(graph, layer):
	set_scaling_factor(layer, True)

def downscale_graph(graph, layer):
	set_scaling_factor(layer, False)


def upscale_positions(positions, layer):
	return scale_positions(positions, set_scaling_factor(3, True))


def downscale_positions(positions, layer):
	return scale_positions(positions, set_scaling_factor(3, False))

def main(graph, layer):
	build_position_dictionary(graph, set_scaling_factor(3, False))
	#build_rescaled_graph(rescale_position_dictionary(build_position_dictionary(graph)), layer)