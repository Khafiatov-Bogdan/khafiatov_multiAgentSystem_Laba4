import typing
import pandas as pd


def get_excel_data(filename, sheet_name) -> typing.List:

    df = pd.read_excel(filename, sheet_name=sheet_name)
    df_index = df.to_dict('index')
    resulted_list = list(df_index.values())
    return resulted_list