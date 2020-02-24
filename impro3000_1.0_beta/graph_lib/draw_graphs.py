
"""
module to print graph. designed to print the complete, raw old inmpro graphs, for overview 
"""
import networkx as nx
import ntpath
import os
import matplotlib.pyplot as plt
import graphviz  
import collections # ordering the dict
from scipy.misc import imread


# SCALING,  keep in mind


def read_and_print(graph, out_path, name):
	""" saves the input graph as .tif with matplotlib """
	print("outpath = ", out_path, " name = ", name)


	# https://networkx.github.io/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_networkx_nodes.html#networkx.drawing.nx_pylab.draw_networkx_nodes
	
	#pasitions = nx.nx_pydot.graphviz_layout(graph)
	print("trying pydot")
	py_dot_graph = nx.drawing.nx_pydot.to_pydot(graph)                 
	#print("getting positions")
	#positions = nx.drawing.nx_pydot.graphviz_layout(graph)


	#building pos_dict:
	print("getting graps vertex dict")
	node_dict_tmp = nx.get_node_attributes(graph, "position") # for item in .. item: node_1
	vertex_dictionary = collections.OrderedDict(sorted(node_dict_tmp.items()))


	print("building postion dictionary")
	pos = {}
	import scale_graph as sg
	for vertex in vertex_dictionary:

		tmp_positions = vertex_dictionary.get(vertex)
		print("HERE COMES THE NONE GML GRAPH CSV TRANSLATION: -- ", tmp_positions)
		#scaled_tmp_positions = sg.downscale_positions(tmp_positions, 3)
		
		#pos[vertex] = tmp_positions
		#print("scaled pos in view: ", scaled_tmp_positions)
		
		#pos[vertex] = scaled_tmp_positions
		pos[vertex] = tmp_positions



	

	#nx.draw(graph, pos=pos, zorder=1, node_size=30, alpha=0.7)
	
	#plt.imshow(img, zorder=0, alpha=0.3)
	nx.draw_networkx(graph, zorder=0, pos=pos, node_size=0.05, node_color="blue", alpha=0.7, width=0.05,  with_labels=False)
	#
	plt.grid("on")
	#
	#plt.show()
	# https://www.infobyip.com/detectmonitordpi.php
	# envy: 178 
	plt.savefig(out_path + name + ".tiff", dpi=1000)
	plt.clf() # clear figure


def main(graph, out_path, name):
	read_and_print(graph, out_path, name)



if __name__ == '__main__':
	main(graph, out_path, name)