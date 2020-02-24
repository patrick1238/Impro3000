"""
Module to calculate all k-communites on given graph and with given k-value.
returns a list of communites; each community list contains all its' vertices.
the term vertex equals the term node -> networkx's documentation works with nodes.

@author: Henrik Gollek

"""

import networkx as nx
import itertools as it
import collections # ordering the dict
import matplotlib.pyplot as plt 
import csv
import numpy as np





node_dict_tmp = nx.get_node_attributes(graph, "position") # for item in .. item: node_1
vertex_dictionary = collections.OrderedDict(sorted(node_dict_tmp.items()))
community_list = [] #[[node_1, node_2], [node_3], ...] # soll ein set werden
in_community_dict = {}
graph = None
k_value = None
for vertex in vertex_dictionary:
	in_community_dict[vertex]=False


	

def get_edges(node):
	# get a list of all edges connected to the node:
	return graph.edges(node) # [('node_0', 'node_1') ... ] # second value in edge list alwys the neighbour node



def get_neighbours(node):
	# get all neighbours to the node, using edges. second value in edge list always the neighbour node:
	edges = get_edges(node)
	neighbours = []
	for edge in edges:
		neighbours.append(edge[1])
	neighbours.sort()
	return neighbours


def get_non_community_neighbours_to_vertex(vertex, local_community):
	""" return all vertices not adjacent to input vertex """
	neighbours_to_vertex = []
	all_neighbours = get_neighbours(vertex)
	for neighbour in all_neighbours:
		if neighbour not in local_community:
			neighbours_to_vertex.append(neighbour)
	return neighbours_to_vertex


def is_clique(nodes): # nodes is a list ['node_1', 'node_2',  ...]
	# checks for list of nodes wether they form a clique
	if len(nodes) < k_value:
		return False
	else:
		counter = 0
		for edge_node_int in range(0, len(nodes)-1): # -1 ? 
			edges = get_edges(nodes[edge_node_int])
			counter +=1
			connected_nodes = [] # list with all neighbours connected to the current check node 
			for edge_tupel in edges:
				connected_nodes.append(edge_tupel[1])
			for check_node_int in range(counter, len(nodes)):
				if not nodes[check_node_int] in connected_nodes:
					return False
		return True


def get_community_neighbours(node):
	# get all nodes that are 1. right and under the node, 2. not in a community // use for seed_clique only:
	all_neighbours = get_neighbours(node)
	community_neighbours = []
	for neighbour in all_neighbours:
		if not node_in_any_community(neighbour):
			community_neighbours.append(neighbour)
	return community_neighbours



def node_in_any_community(vertex):
	""" check if the vertex is in any community. returns True if this is the case, False if not. """
	return in_community_dict.get(vertex)




def seed_clique(vertex):
	""" create a seed clique to percolate from:
	 	does not check if enough vertices are left to create clique 
	 	-> has to be checked beforehand when the function is called 
	 	returns a new seed_community if a clique can be formed;
	 	returns none if no further clique can be found. """
	if not node_in_any_community(vertex):
		community_neighbours = get_community_neighbours(vertex)			
		if len(community_neighbours) >= k_value - 1:
			possible_permutations_temp = it.combinations(community_neighbours, k_value-1)
			for permutation in possible_permutations_temp:
				permutation = list(permutation)

				all_seed_vertices = True
				for seed_vertex in permutation:
					if node_in_any_community(seed_vertex):
						all_seed_vertices = False
				if all_seed_vertices:
				

					permutation.append(vertex)
					if is_clique(permutation):
						permutation.sort()
						return permutation
	return None

def get_neighbours_in_community(vertex, local_community):
	""" retuns all the neighbouring vertices to the input vertex that are in the input community """
	community_vertices = []
	for potential_vertex in get_neighbours(vertex):
		if potential_vertex in local_community: 
			community_vertices.append(potential_vertex)	
	return community_vertices


def get_bronk_nodes(node, node_to_check, local_community):
	""" initiates the vertex_list for the bron-kerbosch-algorithm """
	node_neighbours = get_neighbours_in_community(node, local_community)  
	node_tc_neighbours = get_neighbours_in_community(node_to_check, local_community) 
	bronk_nodes = set(node_neighbours).intersection(set(node_tc_neighbours))
	return bronk_nodes


def bron_kerbosch_community(r_set, p_set, x_set, local_community):
	""" the actual bron-kerbosch-algorithm of the check_via_bronk function.
		returns the first clique thats' size equals the k-value. """
	if (len(p_set) == 0 and len(x_set) == 0) or len(r_set) == k_value: # don't go further if a big enough clique has been detected
		return r_set
	for vertex in p_set:
		neighbour_set = set(get_neighbours_in_community(vertex, local_community))
		r_set.add(vertex)
		return bron_kerbosch_community(r_set, p_set.intersection(neighbour_set), x_set.intersection(neighbour_set), local_community)
		p_set.discard(vertex) # vertex von p abziehen 
		x_set.add(vertex) # vertex zu x hinzufügen 


def check_community_membership_via_bronk(node, node_to_check, local_community):
	""" checks for the input vertex, if it can be added to the current community. utelizes the bron-kerbosch-algorithm for this task. """
	r_set = {node, node_to_check} # potential clique
	x_set = {node, node_to_check} # vertices already in clique
	p_set = get_bronk_nodes(node, node_to_check, local_community) # vertices in graph : knoten von node in com, knoten con ntc in com
	if len(p_set) < k_value-2:
		return False
	# perform bron-kerbosch:
	bronk_set = bron_kerbosch_community(r_set, p_set, x_set, local_community)
	if bronk_set == None:
		return False
	if len(bronk_set) == k_value:
		return True
	else:
		print("VORSICHT: der fall ist nicht vorgesehen und sollte nicht eintreten!")
		return False



def detect_communities_bronk():
	""" main logic to iterate over all the graphs vertices. and initiate all relevant subsequent calculations and function calls. """
	while_counter = 0
	for global_vertex in vertex_dictionary:
		while_counter += 1
		local_community = seed_clique(global_vertex) # seed clique is the stzart of the new local community
		if local_community != None:
			for community_vertex in local_community:
				potential_community_vertices = get_non_community_neighbours_to_vertex(community_vertex, local_community)
				if potential_community_vertices != None:
					for potential_community_vertex in potential_community_vertices:
						if check_community_membership_via_bronk(community_vertex, potential_community_vertex, local_community):
							local_community.append(potential_community_vertex)
			community_list.append(local_community)
			for vertex in local_community:
				in_community_dict[vertex] = True






################################################################ MAIN ######################################################################

def detect_communities(k_value, cell_graph, arguments):
	""" calls detect_communities_bronk function, that handels all the community calculation.
		returns a list community_dict.  """
	# actual main logic:
	global graph
	global k_value
	graph = cell_graph
	k_value = k_value
	detect_communities_bronk()
	
	community_dict = {}
	if len(community_list) > 0:
		# sort: largest community is first:
		community_list.sort(key = len, reverse=True)
		counter = 0
		# fill community_dict with list of nodes for each community:
		for community in community_list:
			community_dict["community_" + str(counter)] = community
			counter += 1
	return community_dict

		

