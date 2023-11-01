"""
This module includes functions used in the set_index method of the Data class.
Various patterns are required because the result data index depends on
the required data types.
"""
import copy

import numpy as np
import pandas as pd


def from_req(Data, req_no):
    """Copy index from the required data index.

    Args:
        Data (Data): Data object to paste index.
        req_no (int): Indicator number of the required data list to copy index.
    """
    index_cols = Data.info.get_column_name("index")
    if len(index_cols) == 0:
        Data.info.index = pd.DataFrame(columns=index_cols)
        return
    if len(Data.data) == 0:
        return

    index_req = Data.reqs[req_no].info.file_index()[
        index_cols + ["_split"]].drop_duplicates()
    if len(Data.info.index) == 0:
        Data.info.index = index_req
    else:
        index_self = Data.info.index[index_cols + ["_split"]].copy()
        Data.info.index = pd.concat([index_self, index_req]).drop_duplicates()

    Data.info.set_index_file_no()


def from_data(Data):
    """Get index from result pandas.DataFrame data.

    This function can only be used for
    :class:`~slitflow.tbl.table.Table` objects.

    Args:
        Data (Table): Table data containing result :class:`pandas.DataFrame`.
    """
    index_cols = Data.info.get_column_name("index")
    if len(index_cols) == 0:
        Data.info.index = pd.DataFrame(columns=index_cols)
        return
    if len(Data.data) == 0:
        return

    index_split = []
    for i, df in enumerate(Data.data, 1):
        if df is not None:
            df_index = copy.deepcopy(df[index_cols])
            df_index.drop_duplicates(inplace=True)
            df_index["_split"] = i
            index_split.append(df_index[index_cols + ["_split"]])
    index_new = pd.concat(index_split).drop_duplicates()
    if len(Data.info.index) == 0 or \
            Data.info.index.equals(pd.DataFrame({"_split": [1]})):
        Data.info.index = index_new
    else:
        index = pd.merge(
            Data.info.index, index_new, on=index_cols, how="outer")
        if "_split_x" in index.columns:
            index.drop("_split_x", axis=1, inplace=True)
            # fill na of _split_y with 0 and change type to int
            # TODO: Consider remaining split file
            index["_split_y"] = index["_split_y"].fillna(0).astype(int)
            index.rename(columns={"_split_y": "_split"}, inplace=True)
        Data.info.index = index
    Data.info.set_index_file_no()


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


def from_req_plus_color(Data, req_no):
    """Copy index from the required data index.

    Args:
        Data (Data): Data object to paste index.
        req_no (int): Indicator number of the required data list to copy index.
    """
    Data.info.copy_req(req_no, "column")
    req_index_cols = Data.reqs[req_no].info.get_column_name("index")
    index_cols = Data.info.get_column_name("index")
    df_color = pd.DataFrame({"color": np.array([1, 2, 3])})
    if len(index_cols) == 0:
        Data.info.index = df_color
        Data.info.add_column(None, "color", "int32", "no",
                             "Color number 1:R,2:G,3:B")
        Data.info.add_column(0, "intensity", "uint8",
                                "a.u.", "Pixel intensity")
        return

    if "color" not in index_cols:
        Data.info.delete_column(keeps=index_cols)
        Data.info.add_column(None, "color", "int32", "no",
                             "Color number 1:R,2:G,3:B")
        Data.info.add_column(0, "intensity", "uint8",
                                "a.u.", "Pixel intensity")
        index_cols = Data.info.get_column_name("index")

    if len(Data.data) == 0:
        return

    index_req = Data.reqs[req_no].info.file_index()[
        req_index_cols + ["_split"]].drop_duplicates()
    dfs = []
    for _, row in index_req.iterrows():
        df_index = pd.DataFrame([row]).reset_index(drop=True)
        df = pd.concat([df_index, df_color], axis=1)
        df = df.fillna(method="ffill").astype(int)
        dfs.append(df[index_cols + ["_split"]])
    index_req = pd.concat(dfs)

    if len(Data.info.index) == 0:
        Data.info.index = index_req
    else:
        index_self = Data.info.index[index_cols + ["_split"]].copy()
        last_split = index_self["_split"].max()
        index_self["_split"] = last_split + 1
        Data.info.index = pd.concat([index_self, index_req]).drop_duplicates()

    Data.info.set_index_file_no()


def set_color_index(Data, req_no, index_depth):
    """Set color index.

    The color index is a number to represent color. 1:R, 2:G, 3:B.

    """
    Data.info.copy_req(req_no, "column")
    index_names = Data.info.get_column_name("index")
    Data.info.delete_column(keeps=index_names[:index_depth])
    Data.info.add_column(None, "color", "int32", "no",
                         "Color number 1:R,2:G,3:B")
    Data.info.add_column(0, "intensity", "uint8",
                            "a.u.", "Pixel intensity")
    Data.info.index = Data.reqs[req_no].info.index.copy()
    dfs = []
    df_color = pd.DataFrame({"color": np.array([1, 2, 3])})
    if len(Data.info.index) == 0:
        Data.info.index = df_color
    else:
        for _, row in Data.info.index.iterrows():
            df_index = pd.DataFrame([row]).reset_index(drop=True)
            df = pd.concat([df_index, df_color], axis=1)
            dfs.append(df.fillna(method="ffill"))
        Data.info.index = pd.concat(dfs).astype(int)
    Data.info.set_index_file_no()


def select_param(Data, SelectParam):
    """Set index from the result of the SelectParam class."""
    index = Data.info.index
    mask_col = Data.info.get_param_value("mask_col")
    temp_index_list = []
    for i, df in enumerate(SelectParam._temp_index):
        df = df[df[mask_col] > 0]
        df = df.drop(columns=mask_col).drop_duplicates()
        if len(index) == 0:
            df["_split"] = i + 1
        elif index["_split"].max() == 0:
            df["_split"] = i + 1
        else:
            df["_split"] = index["_split"].max() + i + 1
        temp_index_list.append(df)
    temp_index = pd.concat(temp_index_list)

    if len(index) == 0 or index.equals(pd.DataFrame({"_split": [1]})):
        Data.info.index = temp_index
    else:
        Data.info.index = pd.concat([index, temp_index])
    Data.info.set_index_file_no()
    SelectParam._temp_index = []
