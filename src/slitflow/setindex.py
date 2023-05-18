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
    index_req = Data.reqs[req_no].info.file_index()[
        index_cols].drop_duplicates()
    if len(Data.info.index) > 0:
        index_self = Data.info.index[index_cols]
        Data.info.index = pd.concat([index_self, index_req]).drop_duplicates()
    else:
        Data.info.index = index_req
    Data.info.set_index_file_no()


def from_data(Data):
    """Get index from result pandas.DataFrame data.

    This function can only be used for
    :class:`~slitflow.tbl.table.Table` objects.

    Args:
        Data (Table): Table data containing result :class:`pandas.DataFrame`.
    """
    index_cols = Data.info.get_column_name("index")
    if (len(index_cols) > 0) & (len(Data.data) > 0):
        index = pd.concat(Data.data)[index_cols].drop_duplicates()
        if len(Data.info.index) == 0:
            Data.info.index = pd.DataFrame(columns=index_cols)
        Data.info.index = pd.merge(
            Data.info.index, index, on=index_cols, how="outer")
        Data.info.set_index_file_no()
    else:
        # for split data with no data
        Data.info.index = pd.DataFrame(columns=index_cols)


def from_req_plus_data(Data, req_no):
    """Copy index from required data index and result pandas.DataFrame.

    This function can only be used for
    :class:`~slitflow.tbl.table.Table` objects. This function is not
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
