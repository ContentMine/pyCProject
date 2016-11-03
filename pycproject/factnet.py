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
        
        Returns: (bipartite_graph, monopartite_graph, fact_nodes, paper_nodes)
        >>> bipartiteGraph, factGraph, paperGraph, fact_nodes, paper_nodes = create_network(CProject, "species", "binomial")
        """
        
        B = nx.Graph()
        labels = {}

        for ctree in CProject.get_ctrees():

            try:
                results = ctree.show_results(plugin).get(query, [])
            except AttributeError:
                continue

            if len(results) > 0:
                # add paper node to one side of the bipartite network
                source = " ".join(ctree.get_title().split())
                B.add_node(source, bipartite=0)
                labels[str(source)] = str(source)

                for result in results:
                    exact = result.get("exact")
                    # add fact node to other side of the bipartite network
                    B.add_node(exact, bipartite=1)
                    labels[exact] = exact.encode("utf-8").decode("utf-8")
                    # add a link between a paper and author
                    B.add_edge(source, exact)

        
        paper_nodes = set(n for n,d in B.nodes(data=True) if d['bipartite']==0)
        fact_nodes = set(B) - paper_nodes
        fact_graph = bipartite.weighted_projected_graph(B, fact_nodes)
        paper_graph = bipartite.weighted_projected_graph(B, paper_nodes)
        
        return B, fact_graph, paper_graph, fact_nodes, paper_nodes
    

def plotGraph(graph, color="blue", figsize=(12, 8), layout='neato'):
    """
    Layout http://stackoverflow.com/questions/21978487/improving-python-networkx-graph-layout

    dot - "hierarchical" or layered drawings of directed graphs. This is the default tool to use if edges have directionality.
    neato - "spring model'' layouts. This is the default tool to use if the graph is not too large (about 100 nodes) and you don't know anything else about it. Neato attempts to minimize a global energy function, which is equivalent to statistical multi-dimensional scaling.
    fdp - "spring model'' layouts similar to those of neato, but does this by reducing forces rather than working with energy.
    sfdp - multiscale version of fdp for the layout of large graphs.
    twopi - radial layouts, after Graham Wills 97. Nodes are placed on concentric circles depending their distance from a given root node.
    circo - circular layout, after Six and Tollis 99, Kauffman and Wiese 02. This is suitable for certain diagrams of multiple cyclic structures, such as certain telecommunications networks.

    """
    labels = {n:n for n in graph.nodes()}
    
    d = nx.degree_centrality(graph)
    
    # layout=nx.spring_layout
    # pos=layout(graph)
    pos = nx.drawing.nx_agraph.graphviz_layout(graph,prog=layout)

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
    

def plotBipartiteGraph(graph, color1="r", color2="b", figsize=(12, 8), layout="neato"):
 
    labels = {n:n for n in graph.nodes()}
    
    d = nx.degree_centrality(graph)
    
    # layout=nx.spring_layout
    # pos=layout(graph)
    pos = nx.drawing.nx_agraph.graphviz_layout(graph,prog=layout)

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

def save_graph(graph, color, filename, figsize=(36, 24), layout="neato"):
    plotGraph(graph, color, figsize=figsize).savefig("%s.svg" %filename, layout=layout)

def create_complete_graph(CProject):
    """
    Creates a multipartite graph consisting of papers on the one hand,
    and all facts of available plugin-results on the other hand.

    Args: CProject
    Returns: (bipartite_graph, monopartite_fact_graph, monopartite_paper_graph, paper_nodes, fact_nodes)
    """
        
    partition_mapping = {"papers":0,
                         "binomial":1, "genus":2, "genussp":3,
                         "carb3":4, "prot3":5, "dna":6, "prot":7,
                         "human":8}
    
    gene = ["human"]
    species = ["binomial"]
    sequence = ["dna", "prot"]
    plugins = {"gene":gene, "species": species, "sequence":sequence}
    
    
    M = nx.Graph()
    labels = {}

    for ctree in CProject.get_ctrees():

        for plugin, types in plugins.items():
            for ptype in types:
        
                try:
                    results = ctree.show_results(plugin).get(ptype, [])
                except AttributeError:
                    continue

                if len(results) > 0:
                    source = " ".join(ctree.get_title().split())
                    if not source in M.nodes():
                        # add paper node to one side of the bipartite network
                        M.add_node(source, bipartite=0)
                        labels[str(source)] = str(source)

                    for result in results:
                        target = result.get("exact")
                        # add fact node to other side of the bipartite network
                        if not target in M.nodes():
                            M.add_node(target, bipartite=1, ptype=ptype)
                            labels[target] = target.encode("utf-8").decode("utf-8")
                        # add a link between a paper and author
                        M.add_edge(source, target)

    paper_nodes = set(n for n,d in M.nodes(data=True) if d.get('bipartite')==0)
    fact_nodes = set(M) - paper_nodes
    fact_graph = bipartite.weighted_projected_graph(M, fact_nodes)
    paper_graph = bipartite.weighted_projected_graph(M, paper_nodes)
    
    return M, fact_graph, paper_graph, fact_nodes, paper_nodes


def plotMultipartiteGraph(M, figsize=(60, 40), layout="neato"):
    partition_mapping = {"papers":0,
                     "binomial":1, "genus":2, "genussp":3,
                     "carb3":4, "prot3":5, "dna":6, "prot":7,
                     "human":8}

    gene = ["human"]
    species = ["binomial"]
    sequence = ["dna", "prot"]
    plugins = {"gene":gene, "species": species, "sequence":sequence}
    color_mapping={"papers":0,
                    "binomial":"green", "genus":2, "genussp":3,
                    "carb3":4, "prot3":5, "dna":"orange", "prot":"cyan",
                    "human":"pink"}
        
    labels = {n:n for n in M.nodes()}
    
    d = nx.degree_centrality(M)
    
    # layout=nx.spring_layout
    # pos=layout(graph)
    pos = nx.drawing.nx_agraph.graphviz_layout(M,prog=layout)

    plt.figure(figsize=figsize)
    plt.subplots_adjust(left=0,right=1,bottom=0,top=0.95,wspace=0.01,hspace=0.01)
    
    paper_nodes = set(n for n,d in M.nodes(data=True) if d.get('bipartite')==0)
    # paper nodes
    nx.draw_networkx_nodes(M,pos,
                            nodelist=paper_nodes,
                            node_color="blue",
                            node_size=[v * 350 for v in d.values()],
                            alpha=0.8)
    
    # nodes
    for plugin, types in plugins.items():
        for ptype in types:
            fact_nodes = set(n for n,d in M.nodes(data=True) if d.get('ptype')==ptype)
            nx.draw_networkx_nodes(M,pos,
                                    nodelist=fact_nodes,
                                    node_color=color_mapping.get(ptype),
                                    node_size=[v * 350 for v in d.values()],
                                    alpha=0.8)
    
    nx.draw_networkx_edges(M,pos,
                           with_labels=True,
                           edge_color="black",
                           width=0.5
                        )
    
    if M.order() < 1000:
        nx.draw_networkx_labels(M,pos, labels)
        
    return plt


def plot_all_facts(G, figsize=(60, 40), layout="neato"):
    partition_mapping = {"papers":0,
                     "binomial":1, "genus":2, "genussp":3,
                     "carb3":4, "prot3":5, "dna":6, "prot":7,
                     "human":8}

    gene = ["human"]
    species = ["binomial"]
    sequence = ["dna", "prot"]
    plugins = {"gene":gene, "species": species, "sequence":sequence}
    color_mapping={"papers":0,
                    "binomial":"green", "genus":2, "genussp":3,
                    "carb3":4, "prot3":5, "dna":"orange", "prot":"cyan",
                    "human":"pink"}
        
    labels = {n:n for n in G.nodes()}
    
    d = nx.degree_centrality(G)
    
    # layout=nx.spring_layout
    # pos=layout(graph)
    pos = nx.drawing.nx_agraph.graphviz_layout(G,prog=layout)

    plt.figure(figsize=figsize)
    plt.subplots_adjust(left=0,right=1,bottom=0,top=0.95,wspace=0.01,hspace=0.01)
    
    # nodes
    for plugin, types in plugins.items():
        for ptype in types:
            fact_nodes = set(n for n,d in G.nodes(data=True) if d.get('ptype')==ptype)
            nx.draw_networkx_nodes(G,pos,
                                    nodelist=fact_nodes,
                                    node_color=color_mapping.get(ptype),
                                    node_size=[v * 350 for v in d.values()],
                                    alpha=0.8)
    
    nx.draw_networkx_edges(G,pos,
                           with_labels=True,
                           edge_color="black",
                           width=0.5
                        )
    
    if G.order() < 1000:
        nx.draw_networkx_labels(G,pos, labels)
        
    return plt