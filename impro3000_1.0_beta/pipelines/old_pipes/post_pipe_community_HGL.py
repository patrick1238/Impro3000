# post pipe for communities - master final

import sys

probabilistic = True 	# else graph will be build deterministic
k_value = 6				# clique size to take into account when building communities
expansion_value = 100	# expansion in pixles on layer 3 from the convex hulls


if probabilistic:
	graph_layout = "probabilistic"
else:
	graph_layout = "deterministic"


####################################################################################


def main(nuclei_graph, cellobject_graph, impro_path, in_path, arguments):
	print("-- entering postprocessing pipeline, get exited --")
	#in_path = arguments["input_path"]
	sys.path.append(arguments["impro_path"] + "/imaging_lib")
	import communities_and_cell_free_tissue
	communities_and_cell_free_tissue.main(nuclei_graph, cellobject_graph, impro_path, in_path, arguments, probabilistic, k_value, expansion_value, graph_layout)


