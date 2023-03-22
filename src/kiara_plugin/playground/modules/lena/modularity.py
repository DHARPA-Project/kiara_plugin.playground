from kiara.api import KiaraModule, ValueMapSchema
import networkx as nx
from networkx.algorithms import community
from operator import itemgetter

from kiara_plugin.network_analysis.models import NetworkData

KIARA_METADATA = {
    "authors": [
        {"name": "Lena Jaskov", "email": "helena.jaskov@uni.lu"},
    ],
    "description": "Kiara modules for: network_analysis",
}

class ModularityCommunity(KiaraModule):
    """Calculate modularity for each node and attach modularity group number to node list as attribute.

    This is a density-based algorithm that can identify clusters within connected components.
    """
    
    _module_type_name = 'compute.modularity_group'

    def create_inputs_schema(
        self,
    ) -> ValueMapSchema:

        result = {
            "network_data": {
                "type": "network_data",
                "doc": "The network data to analyze.",
            }
        }
        return result
    
    def create_outputs_schema(self):
        return {
            "modularity_network": {
                "type": "network_data",
                "doc": "Updated network data with modularity group assigned as a node attribute."
            }
        }
    
    def process(self, inputs, outputs):
        edges = inputs.get_value_obj('network_data')

        network_data: NetworkData = edges.data

        G = network_data.as_networkx_graph(nx.Graph)

        communities = community.greedy_modularity_communities(G)

        modularity_dict = {} 
        for i,c in enumerate(communities): # Loop through the list of communities, keeping track of the number for the community
            for name in c: # Loop through each node in a community
                modularity_dict[name] = i # Create an entry in the dictionary for the node, where the value is which group it belongs to.

        nx.set_node_attributes(G, modularity_dict, 'Modularity_Group')

        attribute_network = NetworkData.create_from_networkx_graph(G)
        
        outputs.set_values(modularity_network=attribute_network)