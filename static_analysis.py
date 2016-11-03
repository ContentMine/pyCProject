#!/bin/env python3
# -*- coding: utf-8 -*-

"""
Runs a standard summarization and visualization workflow on a CProject.
"""

import networkx as nx
from pycproject.factnet import create_complete_graph, create_network, plotGraph, save_graph
from pycproject.readctree import CProject
import pandas as pd
import argparse
import os
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser(description='Runs a standard summarization and visualization workflow on a CProject.')
parser.add_argument('--input', dest='inputfolder', help='relative or absolute path of the CProject folder')
parser.add_argument('--output', dest='outputfolder', help='relative or absolute path of the output folder')
parser.add_argument('--action', dest='action', help='what to do', nargs="+", default=[])
parser.add_argument('--plugin', dest='plugin', help='plugin and type to run action on, e.g. "species" "binomial"', nargs="+", default=[])
args = parser.parse_args()


def export_subgraphs(graph, how_many):
    start_with = 0 # pick a number between 1 and 50
    how_many = how_many # choose the number of communities you want to plot between 1 and 5. More takes a lot of space in your notebook
    subgraphs = sorted(nx.connected_component_subgraphs(graph), key=len, reverse=True)[start_with:start_with+how_many]
    for sg in subgraphs:
        degreeCent = nx.algorithms.degree_centrality(sg)
        maxdegreenode = max(degreeCent, key=degreeCent.get)
        print(maxdegreenode)
        #plotGraph(sg, "orange").show() # choose a color, e.g. red, blue, green, ...
        save_graph(sg, "orange", figsize=(12, 12), filename=os.path.join(args.outputfolder, maxdegreenode))


def visualize_timeline(cproject):
    data = {}
    for ctree in cproject:
        try:
            data[ctree.ID] = ctree.get_pdate()
        except:
            continue
    df = pd.DataFrame().from_dict(data, orient="index")
    df.index = pd.to_datetime(df[0])
    year_counts = df.groupby(df.index.to_period("M")).count()
    year_counts.columns = ["Papers per year"]
    fig = year_counts.plot()
    plt.savefig("Papers_per_year.svg")
    plt.close()


def main(args):
    inputfolder = args.inputfolder
    outputfolder = args.outputfolder
    project = CProject(os.getcwd(), inputfolder)
    if len(args.plugin) == 2:
        filename = "-".join(args.plugin)
        complete_graph, fact_graph, paper_graph, fact_nodes, paper_nodes = create_network(project, args.plugin[0], args.plugin[1])
        nx.write_gml(complete_graph, os.path.join(outputfolder, "-".join([filename, "complete_graph.gml"])))
        nx.write_gml(fact_graph, os.path.join(outputfolder, "-".join([filename, "fact_graph.gml"])))
        nx.write_gml(paper_graph, os.path.join(outputfolder, "-".join([filename, "paper_graph.gml"])))
        print("The number of papers in the network: ", len(paper_nodes))
        print("The number of facts: ", len(fact_nodes))
    if "completeGraph" in args.action:
        filename = "complete-graph"
        complete_graph, fact_graph, paper_graph, fact_nodes, paper_nodes = create_complete_graph(project)
        nx.write_gml(complete_graph, os.path.join(outputfolder, "complete_graph.gml"))
        nx.write_gml(fact_graph, os.path.join(outputfolder, "fact_graph.gml"))
        nx.write_gml(paper_graph, os.path.join(outputfolder, "paper_graph.gml"))
        print("The number of papers in the network: ", len(paper_nodes))
        print("The number of facts: ", len(fact_nodes))
    if "plotFactNetwork" in args.action:
        save_graph(fact_graph, color="blue", filename=os.path.join(outputfolder, "-".join([filename, "fact-graph"])))
    if "plotPaperNetwork" in args.action:
        save_graph(paper_graph, color="blue", filename=os.path.join(outputfolder, "-".join([filename, "paper-graph"])))
    if "plotSubgraphs" in args.action:            
        print("Exporting subgraphs.")
        export_subgraphs(fact_graph, 5)
    if "visualizeTimeline" in args.action:
        print("Visualizing paper count timeline.")


if __name__ == '__main__':
    main(args)