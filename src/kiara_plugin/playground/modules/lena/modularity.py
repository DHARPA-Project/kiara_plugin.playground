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

    This networkX based function uses Clauset-Newman-Moore greedy modularity maximization to find the community partition with the largest modularity.

    Modularity community is a density-based community detection method that investigates the structural composition of a network.
    """
    
    _module_type_name = 'compute.modularity_group'

    def create_inputs_schema(
        self,
    ) -> ValueMapSchema:

        result = {
            "network_data": {
                "type": "network_data",
                "doc": "The network data to analyze.",
                "optional": False,
            },
            "number_of_communities":{
                "type": "integer",
                "doc": "Number of communities into which the network should be partitioned. This is a user defined number that can be above or below maximum modularity.",
                "optional": True,
            }
        }
        return result
    
    def create_outputs_schema(self):
        return {
            "modularity_network": {
                "type": "network_data",
                "doc": "Updated network data with modularity group assigned as a node attribute."
            },
            "maximum_modularity":{
                "type": "integer",
                "doc": "The number of communities at which maximum modularity is reached for this network. If the 'number_of_communities' is manually set, this number might deviate from the manually computed number.",
            }
        }
    
    def process(self, inputs, outputs):
        edges = inputs.get_value_obj('network_data')

        network_data: NetworkData = edges.data

        G = network_data.as_networkx_graph(nx.Graph) #Other graph types will work as well and modularity group distribution can be different with different graph types. Maximum modularity can also be affected by edge weight, but this parameter is currently not set. If the graph consists on many unconnected components, then the modularity groups will mostly coincide with the components. It would then make sense to extract the largest connected component first and to run the modularity module on the largest component.

        number_of_communities = inputs.get_value_data("number_of_communities") #TODO: This integer must be in range [1, G.number_of_nodes()]; otherwise it will throw a networkX error.

        if number_of_communities is None:
            communities = community.greedy_modularity_communities(G)
            maximum_modularity = len(communities)
        else:
            communities = community.greedy_modularity_communities(G, cutoff=number_of_communities, best_n=number_of_communities)
            max_communities = community.greedy_modularity_communities(G)
            maximum_modularity = len(max_communities)

        modularity_dict = {} 
        for i,c in enumerate(communities): # Loop through the list of communities, keeping track of the number for the community
            for name in c: # Loop through each node in a community
                modularity_dict[name] = i # Create an entry in the dictionary for the node, where the value is which group it belongs to.

        nx.set_node_attributes(G, modularity_dict, 'modularity_group')

        attribute_network = NetworkData.create_from_networkx_graph(G)
        
        outputs.set_values(modularity_network=attribute_network, maximum_modularity=maximum_modularity)