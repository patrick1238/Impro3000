"""
Main pipeline to run a correlation between eosínophilc regions and cellclusters, aka communities.
The pipeline: 
- creates all directories needed; 
- maps the svs-images to their corresponding cellgraphs (mapping-file has to be provided); 
- initiates the creation of probabilistic / deterministic the cellgraps;
- loads roi and eosinophilic regions as binary images;
- initiates the community calculation
- initiates the corraltion between eosínophilc regions and communities
Detailed information can be found within the main method.

@author: Henrik Gollek

"""


import sys
import os
import csv
import networkx as nx


probabilistic = None 	# passed over from postprocessing-pipeline
k_value = None			# passed over from postprocessing-pipeline
expansion_value = None	# passed over from postprocessing-pipeline
graph_layout = None		# passed over from postprocessing-pipeline

cutoff = 24				# communities below cutoff will not be considered during plotting results


####################################################################################



def create_directories(arguments):
	""" creating directories and storing the paths in arguments for easy access -> these will be accessible in get communities as well, keep in mind :) """
	arguments["communities_dir"] = arguments["results"] + "communities/"
	arguments["k_clique_dir"] = arguments["communities_dir"] + "k_" + str(k_value) + "_" +  graph_layout + "/"	
	arguments["gmls_dir"] = arguments["k_clique_dir"] + "gmls/"
	arguments["mapped_images_dir"] = arguments["k_clique_dir"] + "mapped_images/"
	arguments["cell_free_results_dir"] = arguments["k_clique_dir"] + "cell_free_results/"

	new_paths = [arguments["communities_dir"], arguments["k_clique_dir"], arguments["gmls_dir"], arguments["mapped_images_dir"], arguments["cell_free_results_dir"]]
	for path in new_paths:
		check_for_and_create_dir(path)
	

def check_for_and_create_dir(path):
	""" create directory if not existent """
	if not os.path.exists(path):
		os.mkdir(path)


def get_mapping_list(arguments):
	""" loads the mapping list for images and cellgraphs. requires a mapping-file in csv-format. 
		file strucure: image_name,graph_name """
	print("trying to read:", arguments["input_mapping"])
	mapping_list = []
	with open(arguments["input_mapping"]) as file:
		open_file = csv.reader(file)
		for line in open_file:
			mapping_list.append(list(line))
	return mapping_list


def get_graph_name_to_image(arguments, mapping_list):
	""" returns the cellgraph name to the current svs-images """
	for match in mapping_list:
		if (match[0].split(".")[0]) == arguments["img_name"]:
			return match[1]


def get_cell_graph_deterministic(path):
	""" returns a deterministic cellgraph in networkx-foramt.
		function is designed to work with legacy cell-grphs from imporimage-sf. """
	from CellGraph import CellGraph as cg
	cell_graph = cg()
	cell_graph.load_graph_from_improfile(path)
	test_graph = cell_graph.get_nxgraph()
	return test_graph

	
def get_cell_graph_probabilistic(path):	
	""" returns a probabilistic cellgraph in networkx-foramt.
		function is designed to work with legacy cell-grphs from imporimage-sf. """
	from CellGraph import CellGraph as cg
	cell_graph = cg()
	cell_graph.load_vertices_from_improfile(path)
	cell_graph.initiate_edges("Waxmann")
	test_graph = cell_graph.get_nxgraph()
	return test_graph


def save_full_graph(graph, path, name):
	""" saves graph to disk in gml-format """
	import draw_graph
	draw_graph.main(graph, path, name + "_cell_graph_" + graph_layout)
	

def get_communities(graph, out_path, name, arguments):
	""" initiates the calculation of all communities for the current svs-image / its cellgraph. """
	from community_detection import CommunityDetection	
	cod = CommunityDetection(graph, k_value, out_path, name, arguments)
	return cod.main()


def view_and_save_communities(arguments, communities_list, img_path, graph_layout, grayscale, name):
	""" function to map all communities to an image. new image is saved to disk. """
	import view_and_save_communities
	view_and_save_communities.main(arguments, communities_list, img_path, graph_layout, k_value, grayscale, name)


def get_cellfree_percentage_for_community(arguments, communities_list, expansion_value):
	""" initiates the main method of the hull_expansion module. 
		basically correlates the communities and eosinophilic regions. """
	import hull_expansion
	hull_expansion.main(arguments, communities_list, expansion_value)


def apply_cutoff(communities_list):
	""" removes all communities with less vertices than the cutoff-value.
		returns a new community-list. """
	new_list = []
	for item in communities_list:
		if len(item) >= cutoff:
			new_list.append(item)
	return new_list




def main(nuclei_graph, cellobject_graph, impro_path, in_path, arguments, probabilistic_tmp, k_value_tmp, expansion_value_tmp, graph_layout_tmp):
	""" main method. 
		0: initiate global variables, values provided by postprocessing pipeline
		1: create all needed directories
		2: initiate cellgraph calculation (probabilistic/deterministic)
		3: save cellgraph to disk. omit to save time, disk space and ram.
		4: initate community calculation for current image/cellgraph
		5: (only if communities != None) map communities to cd30 and binaray (eosinophilic) images and save to disk.
										 omit to save time and disk space. 
		6: (only if communities != None) initiate the correlation of the communities and eosinophilic regions """

	print("-- entering postprocessing pipeline, get exited --")

	# step 0: set the global variables
	global probabilistic 
	global k_value
	global expansion_value
	global graph_layout
	probabilistic = probabilistic_tmp
	k_value = k_value_tmp
	expansion_value = expansion_value_tmp
	graph_layout  = graph_layout_tmp

	# step 1: create all directories / paths:
	print("[post_pipe] creating directories")
	sys.path.append(arguments["impro_path"] + "/graph_lib")
	sys.path.append(arguments["impro_path"] + "/imaging_lib/community_lib")
	create_directories(arguments)

	# step 2: get cell graph either probabilistic or deterministc:
	print("[post_pipe] building graph")
	mapping_list = get_mapping_list(arguments)
	graph_name = get_graph_name_to_image(arguments, mapping_list)
	if probabilistic:
		nx_graph = get_cell_graph_probabilistic(arguments["input_graph"] + graph_name)
	else:
		nx_graph = get_cell_graph_deterministic(arguments["input_graph"] + graph_name)
	print(nx.info(nx_graph))

	# step 3: save entire graph, scaled to layer 3:
	print("[post_pipe] saving graph as img")
	save_full_graph(nx_graph, arguments["results"], arguments["img_name"])

	# step 4: community detection via clique percolation:
	print("[post_pipe] computing communities with k = " + str(k_value))
	communities_list_raw = get_communities(nx_graph, arguments["gmls_dir"], arguments["img_name"], arguments)

	if communities_list_raw == None:
		print("!! No Communities detected !!")
	else:

		communities_list = apply_cutoff(communities_list_raw)
		# step 5: view / save communities mapped on to original layer 3 and cell_free / binary layer 3:
		# mapping to cd30:
		print("[post_pipe] mapping communities to layer 3")
		view_and_save_communities(arguments, communities_list, arguments["results"] + arguments["img_name"] + "_3_0_0.tif", graph_layout, False, "layer3") # boolen for grayscale on / off
		# mapping to eosinophilic binary image:
		print("[post_pipe] mapping communities to layer 3 cell free, binary")
		view_and_save_communities(arguments, communities_list, arguments["results"] + "cell_free_binary.tif", graph_layout, True, "layer3_cellfree")

		# step 6: hull_expansion -> convex hull, outer hull and everything in between (aka the results of my thesis):
		print("[post_pipe] getting cell free percentages around communities")
		get_cellfree_percentage_for_community(arguments, communities_list, expansion_value) 

