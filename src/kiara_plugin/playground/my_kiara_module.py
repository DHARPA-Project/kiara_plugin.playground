from kiara.api import KiaraModule

class TutorialModule(KiaraModule):

    def create_inputs_schema(self):
        return {
            "table_input": {
                "type": "table"
            }
        }

    def create_outputs_schema(self):
        return {
            "table_output": {
                "type": "table"
            }
        }

    def process(self, inputs, outputs) -> None:
        pass
