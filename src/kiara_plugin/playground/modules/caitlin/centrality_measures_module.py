from kiara.api import KiaraModule
import networkx as nx
from operator import itemgetter
import pandas as pd

from kiara_plugin.network_analysis.models import NetworkData


KIARA_METADATA = {
    "authors": [
        {"name": "Caitlin Burge", "email": "caitlin.burge@uni.lu"},
    ],
    "description": "Kiara modules for: network_analysis",
}

class Degree_Ranking(KiaraModule):
    """Creates an ordered table with the rank and raw score for degree centrality.
    In an undirected graph, degree centrality measures the number of independent connections each node has.
    
    Uses networkx degree.
    https://networkx.org/documentation/stable/reference/generated/networkx.classes.function.degree.html"""
    
    _module_type_name = 'create.degree_rank_list'
    
    def create_inputs_schema(self):
        return {
            "network_data": {
                "type": "network_data",
                "doc": "The network graph being queried."
            }
        }

    def create_outputs_schema(self):
        return {
            "network_result": {
                "type": "table",
                "doc" : "A table showing the rank and raw score for degree centrality."
            },
            "centrality_network": {
                "type": "network_data",
                "doc": "Updated network data with degree ranking assigned as a node attribute."
            }
        }

    def process(self, inputs, outputs):
        edges = inputs.get_value_obj('network_data')

        network_data: NetworkData = edges.data  # check the source for the NetworkData class to see what
                                                # convenience methods it can give you:
                                                # https://github.com/DHARPA-Project/kiara_plugin.network_analysis/blob/develop/src/kiara_plugin/network_analysis/models.py#L52

        G = network_data.as_networkx_graph(nx.Graph)
        
        MG = network_data.as_networkx_graph(nx.MultiDiGraph)
        
        graph = nx.DiGraph()
        for u,v,data in MG.edges(data=True):
            w = data['weight'] if 'weight' in data else 1.0
            if graph.has_edge(u,v):
                graph[u][v]['weight'] += w
            else:
                graph.add_edge(u, v, weight=w)
        
        def result_func(list):
            rank, count, previous, result = (0, 0, None, {})
            for key, num in list:
                count += 1
                if num != previous:
                    rank += count
                    previous = num
                    count = 0
                result[key] = num, rank
            return result
        
        degree = {}
        for node in G:
            degree[node]= G.degree(node)
        nx.set_node_attributes(G, degree, 'Degree Score')
        
        weight_degree = {}
        for node in graph:
            weight_degree[node]= graph.degree(node)
        nx.set_node_attributes(G, weight_degree, 'Weighted Degree Score')
            
        sorted_dict = [[item[1][1], item [0], item[1][0]] for item in sorted(result_func(sorted(degree.items(), key=itemgetter(1), reverse =True)).items(), key=itemgetter(1), reverse =True)]

        df= pd.DataFrame(sorted_dict)
        df.columns = ['Rank', 'Node', 'Score']
        
        attribute_network = NetworkData.create_from_networkx_graph(G)
        
        outputs.set_values(network_result=df, centrality_network=attribute_network)

class Betweenness_Ranking(KiaraModule):
    """Creates an ordered table with the rank and raw score for betweenness centrality.
    In an undirected graph, betweenness centrality measures the percentage of all shortest paths that a node appears on, therefore measuring the likeliness that a node may act as a connector or 'intermediary'.
    
    Uses networkx.betweenness_centrality()
    https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.betweenness_centrality.html#networkx.algorithms.centrality.betweenness_centrality"""
    
    _module_type_name = 'create.betweenness_rank_list'
    
    def create_inputs_schema(self):
        return {
            "network_data": {
                "type": "network_data",
                "doc": "The network graph being queried."
            }
        }

    def create_outputs_schema(self):
        return {
            "network_result": {
                "type": "table",
                "doc" : "A table showing the rank and raw score for betweenness centrality."
            },
            "centrality_network": {
                "type": "network_data",
                "doc": "Updated network data with betweenness ranking assigned as a node attribute."
            }
        }

    def process(self, inputs, outputs):
        edges = inputs.get_value_obj('network_data')

        network_data: NetworkData = edges.data  # check the source for the NetworkData class to see what
                                                # convenience methods it can give you:
                                                # https://github.com/DHARPA-Project/kiara_plugin.network_analysis/blob/develop/src/kiara_plugin/network_analysis/models.py#L52

        G = network_data.as_networkx_graph(nx.Graph)
        
        def result_func(list):
            rank, count, previous, result = (0, 0, None, {})
            for key, num in list:
                count += 1
                if num != previous:
                    rank += count
                    previous = num
                    count = 0
                result[key] = num, rank
            return result
        
        between = nx.betweenness_centrality(G)
        nx.set_node_attributes(G, between, 'Betweenness Score')
        sorted_dict = [[item[1][1], item [0], item[1][0]] for item in sorted(result_func(sorted(between.items(), key=itemgetter(1), reverse =True)).items(), key=itemgetter(1), reverse =True)]
        
        df= pd.DataFrame(sorted_dict)
        df.columns = ['Rank', 'Node', 'Score']
        
        attribute_network = NetworkData.create_from_networkx_graph(G)
        
        outputs.set_values(network_result=df, centrality_network=attribute_network)

class Eigenvector_Ranking(KiaraModule):
    """Creates an ordered table with the rank and raw score for betweenness centrality.
    In an undirected graph, eigenvector centrality measures the extent to which a node is connected to other nodes of importance or influence.
    
    Uses networkx.eigenvector_centrality()
    https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.eigenvector_centrality.html#networkx.algorithms.centrality.eigenvector_centrality"""
   
    _module_type_name = 'create.eigenvector_rank_list'
    
    def create_inputs_schema(self):
        return {
            "network_data": {
                "type": "network_data",
                "doc": "The network graph being queried."
            },
            "iterations": {
                "type" : "integer",
                "default": 1000
            }
        }

    def create_outputs_schema(self):
        return {
            "network_result": {
                "type": "table",
                "doc" : "A table showing the rank and raw score for eigenvector centrality."
            },
            "centrality_network": {
                "type": "network_data",
                "doc": "Updated network data with eigenvector ranking assigned as a node attribute."
            }
        }

    def process(self, inputs, outputs):
        edges = inputs.get_value_obj('network_data')
        iterations = inputs.get_value_data("iterations")

        network_data: NetworkData = edges.data  # check the source for the NetworkData class to see what
                                                # convenience methods it can give you:
                                                # https://github.com/DHARPA-Project/kiara_plugin.network_analysis/blob/develop/src/kiara_plugin/network_analysis/models.py#L52

        G = network_data.as_networkx_graph(nx.Graph)
        
        def result_func(list):
            rank, count, previous, result = (0, 0, None, {})
            for key, num in list:
                count += 1
                if num != previous:
                    rank += count
                    previous = num
                    count = 0
                result[key] = num, rank
            return result
        
        eigenvector = nx.eigenvector_centrality(G, max_iter=iterations)
        nx.set_node_attributes(G, eigenvector, 'Eigenvector Score')
        sorted_dict = [[item[1][1], item [0], item[1][0]] for item in sorted(result_func(sorted(eigenvector.items(), key=itemgetter(1), reverse =True)).items(), key=itemgetter(1), reverse =True)]
        
        df= pd.DataFrame(sorted_dict)
        df.columns = ['Rank', 'Node', 'Score']
        
        attribute_network = NetworkData.create_from_networkx_graph(G)
        
        outputs.set_values(network_result=df, centrality_network=attribute_network)

class Closeness_Ranking(KiaraModule):
    """Creates an ordered table with the rank and raw score for closeness centrality.
    In an undirected graph, closeness centrality measures the average shortest distance path between a node and all reachable nodes in the network.
    
    Uses networkx.closeness_centrality()
    https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.closeness_centrality.html#networkx.algorithms.centrality.closeness_centrality"""
    
    _module_type_name = 'create.closeness_rank_list'
    
    def create_inputs_schema(self):
        return {
            "network_data": {
                "type": "network_data",
                "doc": "The network graph being queried."
            }
        }

    def create_outputs_schema(self):
        return {
            "network_result": {
                "type": "table",
                "doc" : "A table showing the rank and raw score for closeness centrality."
            },
            "centrality_network": {
                "type": "network_data",
                "doc": "Updated network data with closeness ranking assigned as a node attribute."
            }
        }

    def process(self, inputs, outputs):
        edges = inputs.get_value_obj('network_data')

        network_data: NetworkData = edges.data  # check the source for the NetworkData class to see what
                                                # convenience methods it can give you:
                                                # https://github.com/DHARPA-Project/kiara_plugin.network_analysis/blob/develop/src/kiara_plugin/network_analysis/models.py#L52

        G = network_data.as_networkx_graph(nx.Graph)
        
        def result_func(list):
            rank, count, previous, result = (0, 0, None, {})
            for key, num in list:
                count += 1
                if num != previous:
                    rank += count
                    previous = num
                    count = 0
                result[key] = num, rank
            return result
        
        closeness = nx.closeness_centrality(G)
        nx.set_node_attributes(G, closeness, 'Closeness Score')
        sorted_dict = [[item[1][1], item [0], item[1][0]] for item in sorted(result_func(sorted(closeness.items(), key=itemgetter(1), reverse =True)).items(), key=itemgetter(1), reverse =True)]
        
        df= pd.DataFrame(sorted_dict)
        df.columns = ['Rank', 'Node', 'Score']
        
        attribute_network = NetworkData.create_from_networkx_graph(G)
        
        outputs.set_values(network_result=df, centrality_network=attribute_network)
