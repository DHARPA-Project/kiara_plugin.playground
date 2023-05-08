from kiara.api import KiaraModule
import networkx as nx
from kiara_plugin.network_analysis.models import NetworkData

KIARA_METADATA = {
    "authors": [
        {"name": "Caitlin Burge", "email": "caitlin.burge@uni.lu"},
    ],
    "description": "Kiara modules for: network_analysis",
}

class CutPointsList(KiaraModule):
    """Create a list of nodes that are cut-points.
    Cut-points are any node in a network whose removal disconnects members of the network, creating one or more new distinct components.
    
    Uses networkx.articulation_points()
    https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.components.articulation_points.html"""
    
    _module_type_name = 'create.cut_point_list'

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
                "type": "list",
                "doc" : "A list of all nodes that are cut-points."
            },
            "cut_network": {
                "type": "network_data",
                "doc": "Updated network data with eigenvector ranking assigned as a node attribute."
            }
        }

    def process(self, inputs, outputs):
        edges = inputs.get_value_obj('network_data')

        network_data: NetworkData = edges.data  # check the source for the NetworkData class to see what
                                                # convenience methods it can give you:
                                                # https://github.com/DHARPA-Project/kiara_plugin.network_analysis/blob/develop/src/kiara_plugin/network_analysis/models.py#L52

        G = network_data.as_networkx_graph(nx.Graph)  # you can also use nx.DiGraph or other types

        cutpoints = list(nx.articulation_points(G))
        
        cut_dict = {}
        for node in G:
            if node in cutpoints:
                cut_dict[node] = 'Yes'
            else:
                cut_dict[node] = 'No'
                
        nx.set_node_attributes(G, cut_dict, 'Cut Point')

        attribute_network = NetworkData.create_from_networkx_graph(G)
        
        outputs.set_values(network_result=cutpoints, cut_network=attribute_network)



