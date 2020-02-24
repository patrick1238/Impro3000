import sys
import os
import csv
import networkx as nx


def get_graph_name_to_image(arguments, mapping_list):
	for match in mapping_list:
		if (match[0].split(".")[0]) == arguments["img_name"]:
			return match[1]

def get_mapping_list(arguments):
	# csv file that maps graphs to image names -> img,graph
	print("trying to read:", arguments["input_mapping"])
	mapping_list = []
	with open(arguments["input_mapping"]) as file:
		open_file = csv.reader(file)
		for line in open_file:
			mapping_list.append(list(line))
	return mapping_list

def get_cell_graph_deterministic(path):
	# old impro cell graphs:
	from CellGraph import CellGraph as cg
	cell_graph = cg()
	cell_graph.load_graph_from_improfile(path)
	test_graph = cell_graph.get_nxgraph()
	print(nx.info(test_graph))
	#return test_graph

	
def get_cell_graph_probabilistic(path):	
	# old impro cell graphs:
	from CellGraph import CellGraph as cg
	cell_graph = cg()
	cell_graph.load_vertices_from_improfile(path)
	cell_graph.initiate_edges("Waxmann")
	test_graph = cell_graph.get_nxgraph()
	print(nx.info(test_graph))
	#return test_graph


def main(nuclei_graph, cellobject_graph, impro_path, in_path, arguments):

	sys.path.append(arguments["impro_path"] + "/graph_lib")
	sys.path.append(arguments["impro_path"] + "/imaging_lib/community_lib")

	mapping_list = get_mapping_list(arguments)
	graph_name = get_graph_name_to_image(arguments, mapping_list)

	print("GRAPH NAME: ", graph_name)
	print("probabilistic:")
	get_cell_graph_probabilistic(arguments["input_graph"] + graph_name)
	print("deterministic:")
	get_cell_graph_deterministic(arguments["input_graph"] + graph_name)

if __name__ == '__main__':	
	main(nuclei_graph, cellobject_graph, impro_path, in_path, arguments_in)




