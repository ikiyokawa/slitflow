"""
This module includes functions used in the set_reqs method of the Data class.
The required data must be sorted to align the correspondence between the data.
"""
import sys

import numpy as np
import pandas as pd

from .fun.misc import reduce_list as rl
if 'ipykernel' in sys.modules:
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm


def fit_1to0(reqs):
    """Keep reqs[0] data even that doesn't contain in reqs[1].

    This function can be used to render movies with trajectories that some
    frames doesn't contain any trajectories.

    Args:
        reqs (list): List of required data with any data type.

    Returns:
        list: List of selected required data
    """
    index_0 = reqs[0].info.file_index().copy()
    index_1 = reqs[1].info.file_index().copy()
    cols = [col for col in index_0.columns if col in index_1.columns]
    cols = [col for col in cols if col not in ["_file", "_split"]]
    index_0 = index_0[cols].drop_duplicates().reset_index(drop=True)
    index_1 = index_1[cols].drop_duplicates().reset_index(drop=True)

    index_mrg = pd.concat([index_0, index_1], axis=0)
    to_put = index_mrg.duplicated(keep=False).iloc[:len(index_0)]
    pos_put = to_put.reset_index(drop=True).index[to_put].to_list()
    sort_data = [None for _ in range(len(index_0))]
    for pos, data in zip(pos_put, reqs[1].data):
        sort_data[pos] = data
    reqs[1].data = sort_data
    return reqs


def copy_1to0(reqs):
    """Sort reqs[1] according to the reqs[0] data structure.

    This function can be used if reqs[0] is split into multiple files while
    reqs[1] is not. reqs[1] is selected to fit reqs[0] data.

    Args:
        reqs (list): List of required data with any data type.

    Returns:
        list: List of selected required data
    """
    index_0 = reqs[0].info.file_index().copy()
    index_1 = reqs[1].info.file_index().copy()
    index_0 = index_0.groupby(["_file", "_split"]).head(1)
    index_1 = index_1.rename(columns={'_split': '_split_1'})
    index_mrg = index_0.merge(index_1)
    pos_list = index_mrg["_split_1"].values
    sort_data = [None for _ in range(len(index_0))]
    for i, pos in enumerate(pos_list):
        sort_data[i] = reqs[1].data[pos]
    reqs[1].data = sort_data
    return reqs


def and_2reqs(reqs):
    """Drop elements that exist only in one required data.

    Args:
        reqs (list): List of required data with any data type.

    Returns:
        list: List of selected required data
    """
    # Get common columns.
    index_0 = reqs[0].info.file_index().copy()
    index_1 = reqs[1].info.file_index().copy()
    cols = [col for col in index_0.columns if col in index_1.columns]
    cols = [col for col in cols if col not in ["_file", "_split"]]

    # Rename columns to avoid duplication.
    index_0 = index_0.rename(
        columns={"_file": "_file_0", "_split": "_split_0"})
    index_1 = index_1.rename(
        columns={"_file": "_file_1", "_split": "_split_1"})

    # Merge index tables and drop index columns.
    index_mrg = pd.merge(index_0, index_1, on=cols,
                         how="outer").dropna().astype(int)
    filesplit_mrg = index_mrg[["_file_0", "_split_0", "_file_1", "_split_1"]]

    file_nos_0 = np.unique(filesplit_mrg["_file_0"].values)
    file_nos_1 = np.unique(filesplit_mrg["_file_1"].values)

    # Extract index tables for selected files.
    index_file_0 = index_0[index_0["_file_0"].isin(
        file_nos_0)].reset_index(drop=True)
    index_file_1 = index_1[index_1["_file_1"].isin(
        file_nos_1)].reset_index(drop=True)

    # Get file and split columns for each required data.
    index_file = pd.merge(index_file_0, index_file_1, on=cols, how="outer").\
        dropna().astype(int)
    filesplit_file = index_file[
        ["_file_0", "_split_0", "_file_1", "_split_1"]].drop_duplicates()
    filesplit_file_0 = filesplit_file[["_file_0", "_split_0"]]
    filesplit_file_1 = filesplit_file[["_file_1", "_split_1"]]

    # Reset split number for each file.
    dfs = []
    for i, (_, df) in enumerate(index_file_0.groupby(["_file_0", "_split_0"])):
        df.loc[:, "_resplit"] = i
        dfs.append(df)
    index_file_resplit_0 = pd.concat(
        dfs)[["_file_0", "_split_0", "_resplit"]].drop_duplicates()
    filesplit_file_0 = pd.merge(index_file_resplit_0, filesplit_file_0,
                                on=["_file_0", "_split_0"], how="inner")
    filesplit_file_0 = filesplit_file_0.drop("_split_0", axis=1).rename(
        columns={"_resplit": "_split_0"})
    dfs = []
    for i, (_, df) in enumerate(index_file_1.groupby(["_file_1", "_split_1"])):
        df.loc[:, "_resplit"] = i
        dfs.append(df)
    index_file_resplit_1 = pd.concat(
        dfs)[["_file_1", "_split_1", "_resplit"]].drop_duplicates()
    filesplit_file_1 = pd.merge(index_file_resplit_1, filesplit_file_1,
                                on=["_file_1", "_split_1"], how="inner")
    filesplit_file_1 = filesplit_file_1.drop("_split_1", axis=1).rename(
        columns={"_resplit": "_split_1"})

    sort_data_0 = [None for _ in range(len(filesplit_file))]
    for i, pos in enumerate(filesplit_file_0["_split_0"].values):
        sort_data_0[i] = reqs[0].data[pos]
    sort_data_1 = [None for _ in range(len(filesplit_file))]
    for i, pos in enumerate(filesplit_file_1["_split_1"].values):
        sort_data_1[i] = reqs[1].data[pos]

    reqs[0].data = sort_data_0
    reqs[1].data = sort_data_1

    return reqs


def set_cols(index):
    """Return column names without _file and _split columns from index table.

    Args:
        index (pandas.DataFrame): Index table.

    Returns:
        list of str: List of column names
    """
    cols = [col for col in list(index.columns) if col not in [
        "_file", "_split"]]
    return cols


def set_reqs_file_nos(reqs, split_depth):
    """Get file numbers of required split data and save data.

    Args:
        reqs (list of Data): List of split required data.
        split_depth (int): Split depth of result data.

    Returns:
        tuple of list of int: (reqs_file_nos, save_file_nos)
    """
    if len(reqs) == 0:
        return [], []

    # Get column list.
    indexes = []
    cols_list = []
    for req in reqs:
        index = req.info.index
        indexes.append(index)
        cols = list(index.columns)
        cols_list.append(
            [col for col in list(index.columns) if col not in [
                "_file", "_split"]])

    # Get common columns.
    col_common = cols_list[0]
    for cols in cols_list:
        col_common = [col for col in cols if col in col_common]
    col_common = col_common + ["_file"]

    # Set common index table.
    indexes_common = []
    n_cols = []
    for i, index in enumerate(indexes):
        index = index[col_common].drop_duplicates().reset_index(drop=True)
        index = index.rename(columns={"_file": f"_file_{i}"})
        indexes_common.append(index)
        n_cols.append(len(index.columns))

    if all(item == 1 for item in n_cols):  # If no common column is found.
        # e.g. affine transformation using pitch info.
        index_mrg = pd.concat(indexes_common, axis=1).fillna(method='ffill')\
            .astype(int).drop_duplicates().reset_index(drop=True)
        index_mrg = index_mrg.reset_index().rename(columns={'index': '_file'})
        new_col = index_mrg.pop("_file")
        index_mrg.insert(len(index_mrg.columns), "_file", new_col)
    else:
        index_mrg = indexes_common[0]
        for index in indexes_common:
            index_mrg = pd.merge(index_mrg, index, how='outer')

        # Set save file no.
        if split_depth > 0:
            grouped = index_mrg.groupby(rl(col_common[:split_depth]))
            dfs = list(list(zip(*grouped))[1])
            cnt = 0
            dfs_wona = []
            for df in dfs:
                df = df.dropna().copy()
                if len(df) > 0:
                    df.loc[:, "_file"] = cnt
                    cnt += 1
                    dfs_wona.append(df)
            index_mrg = pd.concat(dfs_wona)
        else:
            index_mrg.loc[:, "_file"] = 0
        index_mrg = index_mrg.drop(col_common[:-1], axis=1).dropna()\
            .drop_duplicates().reset_index(drop=True)

    # Get reqs_no as list of integers.
    reqs_no = index_mrg.values[:, :-1].astype(np.float64)
    save_no = index_mrg.values[:, -1].astype(np.float64)
    for row in range(len(save_no) - 1):
        if save_no[row] == save_no[row + 1]:
            save_no[row] = None
    return reqs_no, save_no
