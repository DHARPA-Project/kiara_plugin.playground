from kiara.api import KiaraModule, KiaraModuleConfig, ValueMap, ValueMapSchema, KiaraAPI
from pydantic import Field
import pyarrow as pa
from networkx.readwrite import json_graph



class GetLineageData(KiaraModule):
    """ Get lineage data to display in visualization.
    """

    _module_type_name = "playground.get_lineage_data"

    def create_inputs_schema(
        self,
    ) -> ValueMapSchema:


        inputs = {
            "table": {"type": "table", "doc": "The table for which we need lineage data."}
        }

        return inputs

    def create_outputs_schema(
        self,
    ) -> ValueMapSchema:

        outputs = {
            "lineage_dict": {
                "type": "dict",
                "doc": "The dict containing lineage data.",
            }
        }
        return outputs

    def process(self, inputs: ValueMap, outputs: ValueMap) -> None:

        table_obj = inputs.get_value_obj("table")

        kiara = KiaraAPI.instance()

        graph = table_obj.lineage.module_graph
        nodes = graph.nodes.data()
        augmented_nodes = dict()


        def get_info(node):
            # all this is terribly inefficient
            if node[1]["node_type"] == "operation":
                result = kiara.retrieve_module_type_info(node[1]["module_type"]).dict()
            elif node[1]["node_type"] == "value":
                value_id = node[0][6:]
                v = kiara.get_value(value_id)

                render_result = kiara.render_value(value=v, target_format="string").rendered

                result = {
                    "preview": render_result
                }
            return result

        for idx, node in enumerate(nodes):
            node_dict = {
                "id": node[0],
                "desc": node[1],
                "parentIds": [pred for pred in graph.predecessors(node[0])],
                "info": get_info(node)
            }
            augmented_nodes[idx] = node_dict
        
        outputs.set_value("lineage_dict", augmented_nodes)

