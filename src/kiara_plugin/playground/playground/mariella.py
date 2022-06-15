from kiara import KiaraModule
import pandas as pd
import re
import csv

class FileNameMetadata(KiaraModule):

    def create_inputs_schema(self):
        
        return {
            "table_input": {
                "type": "table",
                "doc": "The corpus for which we want to extract metadata from file names."
            },
            "column_name": {
                "type": "string",
                "doc": "The column containing metadata with LCCN pattern, like: '/sn86069873/1900-01-05/'."
            }
        }

    def create_outputs_schema(self):
        return {
            "table_output": {
                "type": "table",
                "doc": "Augmented table containing extracted metadata."
            },
            "publications_ref": {
                "type": "list",
                "doc": "List of unique publications refs in table."
            },
            "publications_count": {
                "type": "list",
                "doc": "Count of unique publications refs in table."
            }
        }

    def process(self, inputs, outputs) -> None:

        table_obj = inputs.get_value_obj("table_input")
        column_name = inputs.get_value_obj("column_name")

        print(column_name.data)
        

        df = table_obj.data.to_pandas()

         # get publication ref from file name
        def get_ref(file):
            ref_match = re.findall(r'(\w+\d+)_\d{4}-\d{2}-\d{2}_',file)
            return ref_match[0]

        # get date from file name
        def get_date(file):
            date_match = re.findall(r'_(\d{4}-\d{2}-\d{2})_',file)
            return date_match[0]
        
        df['date'] = df['file_name'].apply(lambda x: get_date(x))

        df['publication'] = df[column_name].apply(lambda x: get_ref(x))
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')

        publications = df['publication'].unique().tolist()
        counts = [df['publication'].value_counts().index.to_list(),df['publication'].value_counts().to_list()]

        outputs.set_value("table_output", df)
        outputs.set_value("publications_ref", publications)
        outputs.set_value("publications_count", publications)

        
        



