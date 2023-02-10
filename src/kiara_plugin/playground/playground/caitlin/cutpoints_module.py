from kiara import KiaraModule
import csv
import networkx as nx
from kiara.models.values.value import ValueMap, ValueMapWritable
​
class CutPointsList(KiaraModule):
    _module_type_name = 'create.cut_point_list'
​
    def create_inputs_schema(self):
        return {
            "network_data": {
                "type": "network_data"
            }
        }
​
    def create_outputs_schema(self):
        return {
            "table_output": {
                "type": "list"
            }
        }
​
    def process(self, inputs, outputs):
        edges = inputs.get_value_obj('network_data')
​
        network_data: NetworkData = edges.data  # check the source for the NetworkData class to see what
                                                # convenience methods it can give you:
                                                # https://github.com/DHARPA-Project/kiara_plugin.network_analysis/blob/develop/src/kiara_plugin/network_analysis/models.py#L52
​
        nx_graph_instance = network_data.as_networkx_graph(nx.Graph)  # you can also use nx.DiGraph or other types
​
        cutpoints = list(nx.articulation_points(nx_graph_instance))
​
        outputs.set_value('table_output', cutpoints)
