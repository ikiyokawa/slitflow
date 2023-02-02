"""
This module includes functions used in the set_reqs method of the Data class.
The required data must be sorted to align the correspondence between the data.
"""

import numpy as np
import pandas as pd

from .fun.misc import reduce_list as rl


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
    index_0 = index_0.groupby("_split").head(1)
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
    index_0 = reqs[0].info.file_index().copy()
    index_1 = reqs[1].info.file_index().copy()
    cols = [col for col in index_0.columns if col in index_1.columns]
    cols = [col for col in cols if col not in ["_file", "_split"]]
    index_0 = index_0[cols].drop_duplicates().reset_index(drop=True)
    index_1 = index_1[cols].drop_duplicates().reset_index(drop=True)

    index_mrg = pd.concat([index_0, index_1], axis=0)
    to_pick_0 = index_mrg.duplicated(keep=False).iloc[:len(index_0)]
    reqs_0 = []
    for i in range(len(to_pick_0)):
        if to_pick_0[i]:
            reqs_0.append(reqs[0].data[i])
    to_pick_1 = index_mrg.duplicated(keep=False).iloc[len(index_0):]
    reqs_1 = []
    for i in range(len(to_pick_1)):
        if to_pick_1[i]:
            reqs_1.append(reqs[1].data[i])
    reqs[0].data = reqs_0
    reqs[1].data = reqs_1

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
    indexes = []

    # get column list
    cols_list = []
    for req in reqs:
        index = req.info.index
        cols = list(index.columns)
        indexes.append(index)
        cols_list.append(
            [col for col in list(index.columns) if col not in [
                "_file", "_split"]])

    # get common columns
    col_common = cols_list[0]
    for cols in cols_list:
        col_common = [col for col in cols if col in col_common]
    col_common = col_common + ["_file"]

    # set common index table
    indexes_common = []
    for i, index in enumerate(indexes):
        index = index[col_common].drop_duplicates().reset_index(drop=True)
        index = index.rename(columns={'_file': '_file_' + str(i)})
        indexes_common.append(index)
    index_mrg = indexes_common[0]
    for index in indexes_common:
        index_mrg = pd.merge(index_mrg, index, how='outer')

    # set save file no
    if split_depth > 0:
        grouped = index_mrg.groupby(rl(col_common[:split_depth]))
        dfs = list(list(zip(*grouped))[1])
        for i, _ in enumerate(dfs):
            dfs[i]["_file"] = i
        index_mrg = pd.concat(dfs)
    else:
        index_mrg["_file"] = 0
    index_mrg = index_mrg.drop(col_common[:-1], axis=1).dropna()\
        .drop_duplicates().reset_index(drop=True)

    # get reqs_no as list of integers
    reqs_no = index_mrg.values[:, :-1].astype(np.float64)
    # TODO: (Future) This code reduces repeat load but does not work without
    #   data stashing during set_reqs.
    # for row in range(1, reqs_no.shape[0]):
    #     for col in range(reqs_no.shape[1]):
    #         if reqs_no[row, col] == reqs_no[row - 1, col]:
    #             reqs_no[row, col] = None
    #         elif np.isnan(reqs_no[row - 1, col]):
    #             reqs_no[row, col] = None
    save_no = index_mrg.values[:, -1].astype(np.float64)
    for row in range(len(save_no) - 1):
        if save_no[row] == save_no[row + 1]:
            save_no[row] = None
    return reqs_no, save_no
