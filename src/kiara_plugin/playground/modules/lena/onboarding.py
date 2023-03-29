from kiara.api import KiaraModule, ValueMapSchema
import networkx as nx

from kiara_plugin.network_analysis.models import NetworkData

KIARA_METADATA = {
    "authors": [
        {"name": "Lena Jaskov", "email": "helena.jaskov@uni.lu"},
    ],
    "description": "Kiara modules for: network_analysis",
}

class GmlOnboarding(KiaraModule):
    """This is a preliminary module for onboarding network data from gml files. It will likely be replaced by more generic onboarding modules when those are ready.
    Based on networkX deserialise GML file method: https://networkx.org/documentation/stable/reference/readwrite/generated/networkx.readwrite.gml.read_gml.html#networkx.readwrite.gml.read_gml
    """
    
    _module_type_name = 'onboard.gml_file'

    def create_inputs_schema(
        self,
    ) -> ValueMapSchema:

        result = {
            #"file": {
             #   "type": "file",
              #  "doc": "The source value (of type 'file').",
               # "optional": False,
            #},
            "path": {
                "type": "string",
                "doc": "The path to the local file.",
                "optional": False,
            },
            "label":{
                "type": "string",
                "doc": "The node attribute that holds the 'label' information. Set this input to 'id' when there is no 'label' attribute in gml file.",
                "optional": True,
                "default": "label",
            }
        }
        return result
    
    def create_outputs_schema(self):
        return {
            "network_data": {
                "type": "network_data",
                "doc": "The network/graph data."
            }
        }
    
    def process(self, inputs, outputs):

        input_file = inputs.get_value_data('path')
        gml_file= input_file

        #print(gml_file)
        label = inputs.get_value_data('label')
        #print(label)

        if label is None:
            G = nx.read_gml(gml_file)
            #print("no label")
        else:
            G = nx.read_gml(gml_file, label=label)
            #print("with label")

        network_data = NetworkData.create_from_networkx_graph(G)
        
        outputs.set_values(network_data=network_data)