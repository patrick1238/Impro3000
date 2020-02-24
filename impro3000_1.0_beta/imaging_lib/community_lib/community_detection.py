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


class CommunityDetection():

	def __init__(self, graph, k_value, out_path, name, arguments):
		self.arguments = arguments
		self.out_path = out_path
		self.graph = graph
		self.k_value = k_value
		self.name = name		
		node_dict_tmp = nx.get_node_attributes(graph, "position") # for item in .. item: node_1
		self.vertex_dictionary = collections.OrderedDict(sorted(node_dict_tmp.items()))
		self.community_list = [] #[[node_1, node_2], [node_3], ...] # soll ein set werden
		self.in_community_dict = {}
		for vertex in self.vertex_dictionary:
			self.in_community_dict[vertex]=False


		

	def get_edges(self, node):
		# get a list of all edges connected to the node:
		return self.graph.edges(node) # [('node_0', 'node_1') ... ] # second value in edge list alwys the neighbour node


	def get_single_edges_into_community(self, node, index):
		# get a list of all edges connected to the node that go into the community:
		tupel_list = self.graph.edges(node)
		single_edges = []
		for tupel in tupel_list:
			if tupel[1] in self.community_list[index]: # kante nur hinzufügen wenn sie in community führt
				single_edges.append(tupel[1])
		return single_edges # [('node_0', 'node_1') ... ] # second value in edge list alwys the neighbour node


	def get_neighbours(self, node):
		# get all neighbours to the node, using edges. second value in edge list always the neighbour node:
		edges = self.get_edges(node)
		neighbours = []
		for edge in edges:
			neighbours.append(edge[1])
		neighbours.sort()
		return neighbours


	def get_non_community_neighbours_to_vertex(self, vertex, local_community):
		""" return all vertices not adjacent to input vertex """
		neighbours_to_vertex = []
		all_neighbours = self.get_neighbours(vertex)
		for neighbour in all_neighbours:
			if neighbour not in local_community:
				neighbours_to_vertex.append(neighbour)
		return neighbours_to_vertex


	def is_clique(self, nodes): # nodes is a list ['node_1', 'node_2',  ...]
		# checks for list of nodes wether they form a clique
		if len(nodes) < self.k_value:
			return False
		else:
			counter = 0
			for edge_node_int in range(0, len(nodes)-1): # -1 ? 
				edges = self.get_edges(nodes[edge_node_int])
				counter +=1
				connected_nodes = [] # list with all neighbours connected to the current check node 
				for edge_tupel in edges:
					connected_nodes.append(edge_tupel[1])
				for check_node_int in range(counter, len(nodes)):
					if not nodes[check_node_int] in connected_nodes:
						return False
			return True


	def get_community_neighbours(self, node):
		# get all nodes that are 1. right and under the node, 2. not in a community // use for seed_clique only:
		all_neighbours = self.get_neighbours(node)
		community_neighbours = []
		for neighbour in all_neighbours:
			if not self.node_in_any_community(neighbour):
				community_neighbours.append(neighbour)
		return community_neighbours



	def node_in_any_community(self, vertex):
		""" check if the vertex is in any community. returns True if this is the case, False if not. """
		return self.in_community_dict.get(vertex)
	



	def seed_clique_3(self, vertex):
		""" create a seed clique to percolate from:
		 	does not check if enough vertices are left to create clique 
		 	-> has to be checked beforehand when the function is called 
		 	returns a new seed_community if a clique can be formed;
		 	returns none if no further clique can be found. """
		if not self.node_in_any_community(vertex):
			community_neighbours = self.get_community_neighbours(vertex)			
			if len(community_neighbours) >= self.k_value - 1:
				possible_permutations_temp = it.combinations(community_neighbours, self.k_value-1)
				for permutation in possible_permutations_temp:
					permutation = list(permutation)

					all_seed_vertices = True
					for seed_vertex in permutation:
						if self.node_in_any_community(seed_vertex):
							all_seed_vertices = False
					if all_seed_vertices:
					

						permutation.append(vertex)
						if self.is_clique(permutation):
							permutation.sort()
							return permutation
		return None

	def get_neighbours_in_community(self, vertex, local_community):
		""" retuns all the neighbouring vertices to the input vertex that are in the input community """
		community_vertices = []
		for potential_vertex in self.get_neighbours(vertex):
			if potential_vertex in local_community: 
				community_vertices.append(potential_vertex)	
		return community_vertices
	

	def get_bronk_nodes(self, node, node_to_check, local_community):
		""" initiates the vertex_list for the bron-kerbosch-algorithm """
		node_neighbours = self.get_neighbours_in_community(node, local_community)  
		node_tc_neighbours = self.get_neighbours_in_community(node_to_check, local_community) 
		bronk_nodes = set(node_neighbours).intersection(set(node_tc_neighbours))
		return bronk_nodes


	def bron_kerbosch_community(self, r_set, p_set, x_set, local_community):
		""" the actual bron-kerbosch-algorithm of the check_via_bronk function.
			returns the first clique thats' size equals the k-value. """
		if (len(p_set) == 0 and len(x_set) == 0) or len(r_set) == self.k_value: # don't go further if a big enough clique has been detected
			return r_set
		for vertex in p_set:
			neighbour_set = set(self.get_neighbours_in_community(vertex, local_community))
			r_set.add(vertex)
			return self.bron_kerbosch_community(r_set, p_set.intersection(neighbour_set), x_set.intersection(neighbour_set), local_community)
			p_set.discard(vertex) # vertex von p abziehen 
			x_set.add(vertex) # vertex zu x hinzufügen 


	def check_community_membership_via_bronk(self, node, node_to_check, local_community):
		""" checks for the input vertex, if it can be added to the current community. utelizes the bron-kerbosch-algorithm for this task. """
		r_set = {node, node_to_check} # potential clique
		x_set = {node, node_to_check} # vertices already in clique
		p_set = self.get_bronk_nodes(node, node_to_check, local_community) # vertices in graph : knoten von node in com, knoten con ntc in com
		if len(p_set) < self.k_value-2:
			return False
		# perform bron-kerbosch:
		bronk_set = self.bron_kerbosch_community(r_set, p_set, x_set, local_community)
		if bronk_set == None:
			return False
		if len(bronk_set) == self.k_value:
			return True
		else:
			print("VORSICHT: der fall ist nicht vorgesehen und sollte nicht eintreten!")
			return False



	def detect_communities_bronk(self):
		""" main logic to iterate over all the graphs vertices. and initiate all relevant subsequent calculations and function calls. """
		self.more_to_calculate = True
		while_counter = 0
		for global_vertex in self.vertex_dictionary:
			while_counter += 1
			local_community = self.seed_clique_3(global_vertex) # seed clique is the stzart of the new local community
			if local_community != None:
				for community_vertex in local_community:
					potential_community_vertices = self.get_non_community_neighbours_to_vertex(community_vertex, local_community)
					if potential_community_vertices != None:
						for potential_community_vertex in potential_community_vertices:
							if self.check_community_membership_via_bronk(community_vertex, potential_community_vertex, local_community):
								local_community.append(potential_community_vertex)
				self.community_list.append(local_community)
				for vertex in local_community:
					self.in_community_dict[vertex] = True




	def save_community_information(self):
		""" saves a csv with the follwong information for each community to the disk: 
			1: community number
			2: community size  """
		with open(self.arguments["cell_free_results_dir"] + self.arguments["img_name"] + "_community_results.csv", 'w', newline='') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			for i in range(len(self.community_list)):
				filewriter.writerow(["community_"+str(i), str(len(self.community_list[i]))])

	
	def plot_community_sizes(self):
		""" function to plot all community sizes. """
		lenght_list = []
		for community in self.community_list:
			lenght_list.append(len(community))
		np_length_list = np.asarray(lenght_list)
		unique_values, counts = np.unique(np_length_list, return_counts=True)	
		plt.plot(unique_values, counts)
		print("values:", unique_values)
		print("counts:", counts)
		plt.ylabel('Number of communities', fontsize=18)
		plt.xlabel('Number of vertices in community', fontsize=16)
		plt.savefig(self.arguments["cell_free_results_dir"] + "community_sizes_plot.tif", dpi=200)
		plt.clf()




	def main(self):
		""" calls detect_communities_bronk function, that handels all the community calculation.
			returns a list of communitys, if at least one has been calculated, else None is returned.
			saves every community as gml-file to disk  """
		# actual main logic:
		self.detect_communities_bronk()
		if len(self.community_list) > 0:
			print(" .. sorting ..")
			self.community_list.sort(key = len, reverse=True)

			print("lenght of the community list in main: ", len(self.community_list))
			print("Communities were build with k = ", self.k_value, " cliuqes")
			print("Largest Community found: ", len(self.community_list[0]))

			counter = 0
			return_list = []
			for community in self.community_list:
				com_len = len(community)
				community_graph = self.graph.subgraph(community)
				return_list.append(community_graph)
				# save community as gml-file to disk:
				nx.write_gml(community_graph, self.out_path+"/k_"+str(self.k_value)+"_community_"+str(counter)+"___"+str(com_len)+"_vertices.gml")
				counter += 1
			self.save_community_information()
			self.plot_community_sizes()
			print("\n\n##############################################################################################################")
			return return_list
		else:
			print("no communities detected")
			return None

		

