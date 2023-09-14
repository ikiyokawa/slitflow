"""
This process module includes classes that change table structure such as
rows and columns.
"""

import numpy as np
import pandas as pd

from .table import Table


class MaskFromParam(Table):
    """Create a mask column based on explicit param values.

    Args:
        reqs[0] (Table): The image to select from.
        param["index"] (list of tuple): A list of tuples that contains the
            indices to select. The tuple should be (index of depth=1, index of
            depth=2, ...). If index is None, all indices of the depth are
            selected.
        param["mask_col"] (str, optional): The name of the mask column.
            Defaults to "mask".
        param["split_depth"] (int): The file split depth number.

    Returns:
        Table: A table containing the mask column.
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add param."""
        self.info.copy_req(0)
        self.info.add_column(
            0, param.get("mask_col", "mask"), "int", "num", "Mask")
        self.info.add_param(
            "index_cols", self.info.get_column_name("index"),
            "list", "Index column names")
        self.info.add_param(
            "mask_col", param.get("mask_col", "mask"), "str",
            "Mask column name")
        self.info.add_param(
            "index", param.get("index"), "list", "Indices to select")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Create a mask column based on explicit param values.

        Args:
            reqs[0] (Table): The image to select from.
            param["index"] (list of tuple): A list of tuples that contains the
                indices to select. The tuple should be (index of depth=1, index
                of depth=2, ...). If index is None, all indices of the depth
                are selected.
            param["index_cols"] (list of str): The index column names.
            param["mask_col"] (str, optional): The name of the mask column.
                Defaults to "mask".

        Returns:
            pandas.DataFrame: A table containing the mask column.
        """
        df = reqs[0].copy()
        index_cols = param.get("index_cols")
        mask_col = param.get("mask_col", "mask")
        index = param.get("index", [])

        sel_ary = np.empty((0, len(index_cols)), int)
        idx_ary = df[index_cols].to_numpy()

        for idx_tuple in index:
            depth_ary = idx_ary.copy()
            for depth, idx in enumerate(idx_tuple):
                if type(idx) is int:
                    depth_ary = depth_ary[depth_ary[:, depth] == idx, :]
                elif idx is None:
                    pass
                elif type(idx) is list:
                    # range is not supported for exporting params as json
                    depth_ary_buf = np.empty((0, len(index_cols)), int)
                    for sub_idx in idx:
                        sub_depth_ary = depth_ary.copy()
                        sub_depth_ary = \
                            sub_depth_ary[sub_depth_ary[:, depth]
                                          == sub_idx, :]
                        depth_ary_buf = np.vstack(
                            [depth_ary_buf, sub_depth_ary])
                    depth_ary = depth_ary_buf
            sel_ary = np.vstack([sel_ary, depth_ary])

        mask = pd.DataFrame(sel_ary, columns=index_cols)
        mask = mask.drop_duplicates()
        mask[mask_col] = 1
        df = pd.merge(df, mask, on=index_cols, how="left")
        df[mask_col] = df[mask_col].fillna(0).astype("int")
        return df


class SelectParam(MaskFromParam):
    """Select rows using explicit param values.

    This class creates a mask column based on explicit param values using
    :class:`slitflow.tbl.filter.MaskFromParam` and selects rows using the mask
    column.

    Args:
        reqs[0] (Table): Table for selection.
        param["index"] (list of tuple): List of tuples of index numbers to
            select. Each tuple should be (index of depth=1, index of depth=2,
            ...). If index is None, all indices of the depth is selected.
        param["mask_col"] (str, optional): Column name of the mask column.
            Defaults to "mask".
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Selected Table.
    """
    _temp_index = []

    def __init__(self, info_path=None):
        super().__init__(info_path)
        SelectParam._temp_index = []

    def set_info(self, param={}):
        """Copy info from reqs[0] and add param."""
        MaskFromParam.set_info(self, param)
        self.info.delete_column(self.info.get_param_value("mask_col"))

    @staticmethod
    def process(reqs, param):
        """Select rows using explicit param values.

        Args:
            reqs[0] (pandas.DataFrame): Table for selection.
            param["index"] (list of tuple): List of tuple of index numbers to
                select. The tuple should be (index of depth=1, index of
                depth=2, ...). If index is None, all indices of the depth is
                selected.
            param["mask_col"] (str, optional): Column name of the mask column.
                Defaults to "mask".
            param["index_cols"] (list of str): The index column names.

        Returns:
            Table: Selected Table.
        """
        df_mask = MaskFromParam.process(reqs, param)
        df_sel = df_mask[df_mask[param["mask_col"]] == 1]
        df_sel.reset_index(drop=True, inplace=True)

        # Save the index (multi-process is not available)
        SelectParam._temp_index.append(
            df_mask[param["index_cols"] + [param["mask_col"]]])
        df_sel = df_sel.drop(columns=param["mask_col"])
        return df_sel

    def set_index(self):
        """Set the index based on the saved temporal index.

        File numbers of the _temp_index are added before selecting the index
        not to skip the numbers that is not selected during saving.

        """
        self.info.index = pd.concat(SelectParam._temp_index)
        self.info.set_index_file_no()
        mask_col = self.info.get_param_value("mask_col")
        self.info.index = self.info.index[self.info.index[mask_col] > 0]
        self.info.index = self.info.index.drop(
            columns=mask_col).drop_duplicates()
