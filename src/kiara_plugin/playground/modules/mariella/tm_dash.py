from kiara.api import KiaraModule
from kiara.exceptions import KiaraProcessingException
import pandas as pd
import re
import pyarrow as pa

class FileNameMetadata(KiaraModule):

    _module_type_name = "playground.tm_dash.file_name_metadata"

    def create_inputs_schema(self):
        
        return {
            "table_input": {
                "type": "table",
                "doc": "The corpus for which we want to extract metadata from file names."
            },
            "column_name": {
                "type": "string",
                "doc": "The column containing metadata. In order to work, file names need to comply with LCCN pattern '/sn86069873/1900-01-05/' containing publication reference and date."
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
            # "publications_count": {
            #     "type": "list",
            #     "doc": "Count of unique publications refs in table."
            # }
        }

    def process(self, inputs, outputs) -> None:

        table_obj = inputs.get_value_obj("table_input")
        column_name = inputs.get_value_obj("column_name").data

        df = table_obj.data.to_pandas()

         # get publication ref from file name
        def get_ref(file):
            ref_match = re.findall(r'(\w+\d+)_\d{4}-\d{2}-\d{2}_',file)
            if not ref_match:
                raise KiaraProcessingException(f"Can't process corpus, invalid format for file name: {file}")
            return ref_match[0]

        # get date from file name
        def get_date(file):
            date_match = re.findall(r'_(\d{4}-\d{2}-\d{2})_',file)
            if not date_match:
                raise KiaraProcessingException(f"Can't process corpus, invalid format for file name: {file}")
            return date_match[0]
        
        df['date'] = df['file_name'].apply(lambda x: get_date(x))

        df['publication'] = df[column_name].apply(lambda x: get_ref(x))
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')

        publications = df['publication'].unique().tolist()
        # counts = [df['publication'].value_counts().index.to_list(),df['publication'].value_counts().to_list()]

        outputs.set_value("table_output", df)
        # unique publications references useful at the next step to map publications references with publications names
        outputs.set_value("publications_ref", publications)
        # outputs.set_value("publications_count", counts)



class MapColumn(KiaraModule):

    _module_type_name = "playground.tm_dash.map_column"

    def create_inputs_schema(self):
        
        return {
            "table_input": {
                "type": "table",
                "doc": "The table that we need to augment by mapping column values (for example an id with a name) in a new column."
            },
            "column_name": {
                "type": "string",
                "doc": "The column that needs mapping."
            },
            "mapping_keys": {
                "type": "list",
                "doc": "list containing 2 lists: 1st list contains values to replace, and the second the ones they should be replaced with."
            },
            "output_col_name": {
                "type": "string",
                "doc": "name of the newly created column"
            }
        }

    def create_outputs_schema(self):
        return {
            "table_output": {
                "type": "table",
                "doc": "Augmented table containing new column with mapped values."
            }
        }

    def process(self, inputs, outputs) -> None:

        table_obj = inputs.get_value_obj("table_input")
        column_name = inputs.get_value_obj("column_name").data
        mapping_keys = inputs.get_value_obj("mapping_keys").data
        output_col_name = inputs.get_value_obj("output_col_name").data

        df = table_obj.data.to_pandas()

        df[output_col_name] = df[column_name].replace(to_replace=mapping_keys[0], value=mapping_keys[1])


        outputs.set_value("table_output", df)


class TableSample(KiaraModule):

    _module_type_name = "playground.tm_dash.table_sample"

    def create_inputs_schema(self):
        
        return {
            "table_input": {
                "type": "table",
                "doc": "The table for which we need to create a sample, in order to test the results on a small portion of a table."
            }
        }

    def create_outputs_schema(self):
        return {
            "table_sample": {
                "type": "table",
                "doc": "Random sample of 15 rows for the input table."
            }
        }

    def process(self, inputs, outputs) -> None:

        table_obj = inputs.get_value_obj("table_input")
        
        df = table_obj.data.to_pandas() 
        df_sample = df.sample(n=15,axis=0)
        if '__index_level_0__' in df_sample.columns:
            df_sample = df_sample.drop(['__index_level_0__'],axis=1)
        table_pa = pa.Table.from_pandas(df_sample)
        outputs.set_value("table_sample", table_pa)


class AddColumn(KiaraModule):

    _module_type_name = "playground.tm_dash.add_column"

    def create_inputs_schema(self):
        
        return {
            "table_input": {
                "type": "table",
                "doc": "The table to which we need to append a column."
            },
            "array_input": {
                "type": "array",
                "doc": "The array that needs to be appended as a column."
            }
        }

    def create_outputs_schema(self):
        return {
            "preprocessed_tokens": {
                "type": "table",
                "doc": "The table with the additional column."
            }
        }

    def process(self, inputs, outputs) -> None:

        table_obj = inputs.get_value_obj("table_input")
        array_obj = inputs.get_value_obj("array_input")
        
        df = table_obj.data.to_pandas()
        col = array_obj.data.to_pylist()

        df['preprocessed_tokens'] = col
        
        outputs.set_value("preprocessed_tokens", df)


class VizDataQuery(KiaraModule):

    _module_type_name = "playground.tm_dash.viz_data_query"

    def create_inputs_schema(self):
        
        return {
            "query_type": {
                "type": "string",
                "doc": "The wished data periodicity to display on visualization."
            },
            "column": {
                "type": "string",
                "doc": "The column that contains publication names or ref/id."
            }
        }

    def create_outputs_schema(self):
        return {
            "query": {
                "type": "string",
                "doc": "The query to pass to the sql query module."
            }
        }

    def process(self, inputs, outputs) -> None:

        agg = inputs.get_value_obj("query_type").data
        col = inputs.get_value_obj("column").data

        if agg == 'month':
            query = f"SELECT strptime(concat(month, '/', year), '%m/%Y') as date, {col} as publication_name, count FROM (SELECT YEAR(date) as year, MONTH(date) as month, {col}, count(*) as count FROM data GROUP BY {col}, YEAR(date), MONTH(date))"
    
        elif agg == 'year':
            query = f"SELECT strptime(year, '%Y') as date, {col} as publication_name, count FROM (SELECT YEAR(date) as year, {col}, count(*) as count FROM data GROUP BY {col}, YEAR(date))"
        
        elif agg == 'day':
            query = f"SELECT strptime(concat('01/', month, '/', year), '%d/%m/%Y') as date, {col} as publication_name, count FROM (SELECT YEAR(date) as year, MONTH(date) as month, {col}, count(*) as count FROM data GROUP BY {col}, YEAR(date), MONTH(date), DAY(date))"
        
        outputs.set_value("query", query)



