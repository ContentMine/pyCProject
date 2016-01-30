#!/bin/env python3
# -*- coding: utf-8 -*-

"""
Provides basic network plotting functions for a CProject.
"""

# import network analysis
import networkx as nx
from networkx.algorithms import bipartite

# import drawing library
import matplotlib.pyplot as plt


__author__ = "Christopher Kittel"
__copyright__ = "Copyright 2015"
__license__ = "MIT"
__version__ = "0.0.2"
__maintainer__ = "Christopher Kittel"
__email__ = "web@christopherkittel.eu"
__status__ = "Prototype" # 'Development', 'Production' or 'Prototype'


layout=nx.spring_layout


def create_network(CProject, plugin, query):
        """
        Creates the network between papers and plugin results.
        Plugin may be any of ["regex", "gene", "sequence", "species"]
        Query corresponds to the fact types found by a plugin,
        for "species" it is one of ["binomial", "genus", "genussp"]
        for "sequences" it is one of ["carb3", "prot3", "dna", "prot"]
        for "gene" it is "human"
        for "regex" it is "regexname".
        
        Args: CProject object
              plugin = "string"
              query = "string"
        
        Returns: (bipartite_graph, monopartite_graph, paper_nodes, fact_nodes)
        >>> bipartiteGraph, factGraph, paperNodes, factNodes = create_network(CProject, "species", "binomial")
        """
        
        B = nx.Graph()
        labels = {}

        for ctree in CProject.get_ctrees():

            try:
                results = ctree.show_results(plugin).get(query, [])
            except AttributeError, e:
                print(e)
                continue

            if len(results) > 0:
                # add paper node to one side of the bipartite network
                B.add_node(ctree.ID, bipartite=0)
                labels[str(ctree.ID)] = str(ctree.ID)

                for result in results:
                    exact = result.get("exact")
                    # add fact node to other side of the bipartite network
                    B.add_node(exact, bipartite=1)
                    labels[exact] = exact.encode("utf-8").decode("utf-8")
                    # add a link between a paper and author
                    B.add_edge(ctree.ID, exact)

        
        paper_nodes = set(n for n,d in B.nodes(data=True) if d['bipartite']==0)
        fact_nodes = set(B) - paper_nodes
        G = bipartite.weighted_projected_graph(B, fact_nodes)
        
        return B, G, paper_nodes, fact_nodes
    

def plotGraph(graph, color="r", figsize=(12, 8)):
    
    labels = {n:n for n in graph.nodes()}
    
    d = nx.degree_centrality(graph)
    
    layout=nx.spring_layout
    pos=layout(graph)
    
    plt.figure(figsize=figsize)
    plt.subplots_adjust(left=0,right=1,bottom=0,top=0.95,wspace=0.01,hspace=0.01)
    
    # nodes
    nx.draw_networkx_nodes(graph,pos,
                            nodelist=graph.nodes(),
                            node_color=color,
                            node_size=[v * 250 for v in d.values()],
                            alpha=0.8)
                            
    nx.draw_networkx_edges(graph,pos,
                           with_labels=False,
                           edge_color=color,
                           width=0.50
                        )
    
    if graph.order() < 1000:
        nx.draw_networkx_labels(graph,pos, labels)
    return plt
    

def plotBipartiteGraph(graph, color1="r", color2="b", figsize=(12, 8)):
 
    labels = {n:n for n in graph.nodes()}
    
    d = nx.degree_centrality(graph)
    
    layout=nx.spring_layout
    pos=layout(graph)

    bot_nodes, top_nodes = bipartite.sets(graph)

    plt.figure(figsize=figsize)
    plt.subplots_adjust(left=0,right=1,bottom=0,top=0.95,wspace=0.01,hspace=0.01)
    
    # nodes
    nx.draw_networkx_nodes(graph,pos,
                            nodelist=bot_nodes,
                            node_color=color1,
                            node_size=[v * 350 for v in d.values()],
                            alpha=0.8)
    nx.draw_networkx_nodes(graph,pos,
                            nodelist=top_nodes,
                            node_color=color2,
                            node_size=[v * 350 for v in d.values()],
                            alpha=0.8)
    
    nx.draw_networkx_edges(graph,pos,
                           with_labels=True,
                           edge_color=color1,
                           width=1.0
                        )
    
    if graph.order() < 1000:
        nx.draw_networkx_labels(graph,pos, labels)
        
    return plt

    
def create_subgraph(cproject, B, G, target):
    
    sg = nx.Graph()
    sg.add_node(target)
    
    for ID in B.neighbors(target):
        sg.add_node(ID)
        sg.add_edge(target, ID)
        for author in cproject.get_ctree(ID).get_authors():
            if not author in sg.nodes():
                sg.add_node(author)
            sg.add_edge(ID, author)
            
    for neighbor in G.neighbors(target):
        sg.add_node(neighbor)
        sg.add_edge(target, neighbor)
        for ID in B.neighbors(neighbor):
            sg.add_node(ID)
            sg.add_edge(neighbor, ID)
            for author in cproject.get_ctree(ID).get_authors():
                if not author in sg.nodes():
                    sg.add_node(author)
                sg.add_edge(ID, author)
    
    return sg

def save_graph(graph, color, filename, figsize=(36, 24)):
    plotGraph(graph, color, figsize=figsize).savefig("%s.png" %filename)