from kiara import KiaraModule
import csv
import networkx as nx
from operator import itemgetter
import community
import numpy
import pandas as pd
from kiara.models.values.value import ValueMap, ValueMapWritable

class NetworkInfo(KiaraModule):
    """Return basic information for the newtork graph created, including number of nodes and edges.
    
    Needs to specify if graph is directed or undirected, but will default to undirected."""
    
    _module_type_name = 'get.network_info'
    
    def create_inputs_schema(self):
        return {
            "network_data": {
                "type": "network_data",
                "doc": "The network graph being queried."
            },
            "graph_type": {
                "type": "string",
                "doc": "The graph type: directed or undirected",
                "default": "undirected"
            }
        }

    def create_outputs_schema(self):
        return {
            "network_result": {
                "type": "string",
                "doc" : "Information about the network graph."
            }
        }
    
    def process(self, inputs, outputs):
        edges = inputs.get_value_obj('network_data')
        graph = inputs.get_value_data('graph_type')

        network_data: NetworkData = edges.data  # check the source for the NetworkData class to see what
                                                # convenience methods it can give you:
                                                # https://github.com/DHARPA-Project/kiara_plugin.network_analysis/blob/develop/src/kiara_plugin/network_analysis/models.py#L52
    
        if graph == 'directed':
            G = network_data.as_networkx_graph(nx.DiGraph)
        else:
            G = network_data.as_networkx_graph(nx.Graph)
    
        if nx.is_directed(G) == True:
                info = str(
                'Graph Type: Directed \n' +
                'Number of Nodes: ' + str(nx.number_of_nodes(G)) + '\n'
                'Number of Edges: ' + str(nx.number_of_edges(G)) + '\n'
                'Graph Density Score: ' + str(nx.density(G)) + '\n'
                'Number of Connected Components: ' + str(nx.number_connected_components(G)) + '\n'
                'Number of nodes in Largest Component: ' + str((G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[0])).number_of_nodes()) + '\n'
                'Network Diameter of Largest Component: ' + str(nx.diameter(G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[0]))) + '\n'
                'Average Path Length of Largest Component: ' + str(nx.average_shortest_path_length(G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[0]))) + '\n'
                )
        else:
        	info = str(
        	'Graph Type: Undirected \n' +
        	'Number of Nodes: ' + str(nx.number_of_nodes(G)) + '\n'
        	'Number of Edges: ' + str(nx.number_of_edges(G)) + '\n'
            'Graph Density Score: ' + str(nx.density(G)) + '\n'
            'Number of Connected Components: ' + str(nx.number_connected_components(G)) + '\n'
            'Number of nodes in Largest Component: ' + str((G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[0])).number_of_nodes()) + '\n'
            'Network Diameter of Largest Component : ' + str(nx.diameter(G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[0]))) + '\n'
            'Average Path Length of Largest Component: ' + str(nx.average_shortest_path_length(G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[0])))
                )
        
        outputs.set_value('network_result', info)