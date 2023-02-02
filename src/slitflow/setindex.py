import pandas as pd

def from_data(Data):
    index_cols = Data.info.get_column_name("index")
    index = pd.concat(Data.data)[index_cols].drop_duplicates()
    if hasattr(Data.info, "index"):
        Data.info.index = pd.concat([Data.info.index, index])\
            .drop_duplicates()
    else:
        Data.info.index = index
    if Data.info.index.empty:
        Data.info.index = pd.DataFrame()
    Data.info.set_index_file_no()
