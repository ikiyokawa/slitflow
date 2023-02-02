"""
This module includes functions used in the set_index method of the Data class.
Various patterns are required because the result data index depends on
the required data types.
"""
import pandas as pd


def from_req(Data, req_no):
    """Copy index from the required data index.

    Args:
        Data (Data): Data object to paste index.
        req_no (int): Indicator number of the required data list to copy index.
    """
    index_cols = Data.info.get_column_name("index")
    index_cols = index_cols + ["_split"]
    index = Data.reqs[req_no].info.file_index()[index_cols].drop_duplicates()
    Data.info.index = pd.concat([Data.info.index, index]).drop_duplicates()
    Data.info.set_index_file_no()


def from_data(Data):
    """Get index from result pandas.DataFrame data.

    This function can only be used for
    :class:`slitflow.tbl.table.Table` objects.

    Args:
        Data (Table): Table data containing result :class:`pandas.DataFrame`.
    """
    index_cols = Data.info.get_column_name("index")
    index = pd.concat(Data.data)[index_cols].drop_duplicates()
    Data.info.index = pd.concat([Data.info.index, index]).drop_duplicates()
    Data.info.set_index_file_no()


def from_req_plus_data(Data, req_no):
    """Copy index from required data index and result pandas.DataFrame.

    This function can only be used for 
    :class:`slitflow.tbl.Table` objects. This function is not
    used in general classes.

    Args:
        Data (Data): Data object containing result :class:`pandas.DataFrame` to
            paste index.
        req_no (int): Indicator number of the required data list to copy index.
    """
    index_cols_req = Data.reqs[req_no].info.get_column_name(
        "index") + ["_split", "_file"]
    index_req = Data.reqs[req_no].info.file_index()[
        index_cols_req].drop_duplicates()
    index_cols = Data.info.get_column_name("index")
    index_data = pd.concat(Data.data)[index_cols].drop_duplicates()
    and_list = list(set(index_data) & set(index_req))
    index = pd.merge(index_data, index_req, on=and_list)
    Data.info.index = pd.concat([Data.info.index, index]).drop_duplicates()

# Prepared but not used.
# def and_2reqs(Data):
#     """Drop index rows that exist only in one required data.

#     Args:
#         Data (Data): Result Data object containing required data.
#     """
#     index_0 = Data.reqs[0].info.index.drop(["_file", "_split"], axis=1)
#     index_1 = Data.reqs[1].info.index.drop(["_file", "_split"], axis=1)
#     index = pd.concat([index_0, index_1])
#     Data.info.index = index[index.duplicated()]
