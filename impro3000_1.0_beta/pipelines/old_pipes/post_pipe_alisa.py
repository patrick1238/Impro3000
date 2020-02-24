
import numpy as np
import time

def main(nuclei_graph,cellobject_graph, impro_path, arguments):
    print(time.ctime())
    print("-- entering postprocessing pipeline --")
    #print(cellobject_graph)
    roundness = nuclei_graph.get_attributes_as_array("Roundnesses", "float")
    size = nuclei_graph.get_attributes_as_array("Size", "float")
    circumference = nuclei_graph.get_attributes_as_array("Circumferences", "float")
    ratio = nuclei_graph.get_attributes_as_array("Ratios", "float")
    print("create csv")
    with open("E:/Users/Hodgkin/Desktop/results_alisa/results.csv", "a") as myfile:
    	myfile.write(str(np.mean(circumference))+ ", "+str(np.std(circumference))+ ", "+str(np.mean(roundness))+ ", "+ str(np.std(roundness))+ ", "+str(np.mean(size))+ ", "+ str(np.std(size))+ ", "+str(np.mean(ratio))+ ", "+ str(np.std(ratio))+"\n")
    print("initiate edges")
    #nuclei_graph.initiate_edges("Deterministic")
    print("save_as_gml")
    nuclei_graph.save_as_gml(arguments["results"])
    #cellobject_graph.display()
    nuclei_graph.info()
    print(nuclei_graph.get_graph_mode())