# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 17:18:23 2019

@author: Hodgkin
"""

def main(graph,arguments):
    graph.save_as_gml(arguments["results"])
    graph.colocalize_nodes()
    graph.save_as_impro_coloc_file(arguments["results"])

    #graph.initiate_edges()
    #graph.analyse()
    #graph.save_analysis(arguments["results"])
