import numpy as np
import pandas as pd

from ..tbl.table import Table
from .. import setreqs


class Value(Table):
    """Create mask value column at the coordinate position of each X and Y.

    .. caution::

        The mask image should be split into a single frame image. In other
        words, the shape of reqs[1] in :meth:`process` should be (1, height,
        width).

    Args:
        reqs[0] (Table): Table including X,Y-coordinates. Required params;
            ``length_unit``, ``pitch``.
        reqs[1] (Image): Image stack to pick up intensity.
        param["add_cols"] (list of str, optional): Additional columns to copy
            from required table. If this param is not defined, index columns
            are copied.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Table containing mask value column
    """

    def set_reqs(self, reqs, param):
        """Drop elements that exist only in one required data.
        """
        self.reqs = setreqs.and_2reqs(reqs)

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params from reqs[1].
        """
        self.info.copy_req(0)
        self.info.copy_req(1, "param")
        length_unit = self.info.get_param_value("length_unit")
        calc_cols = ["x_" + length_unit, "y_" + length_unit]
        self.info.add_column(
            0, "mask_val", "float32", "a.u.",
            "Pixel intensity at the coordinate position")
        self.info.add_param(
            "calc_cols", calc_cols, "list of str",
            "Column names for X,Y-coordinate")
        index_cols = self.info.get_column_name("index")
        self.info.add_param("index_cols", index_cols, "list of str",
                            "Columns for index")
        if "add_cols" in param:
            keeps = index_cols + param["add_cols"] + ["mask_val"]
            index_cols = index_cols + param["add_cols"]
        else:
            keeps = index_cols + ["mask_val"]
        self.info.delete_column(keeps=keeps)
        self.info.add_param("index_cols", index_cols, "list of str",
                            "Columns for index")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Create mask value column at the coordinate position of each X and Y.

        Args:
            reqs[0] (pandas.DataFrame): Table including X,Y-coordinate.
            reqs[1] (numpy.ndarray): Numpy 3D array with the shape of
                (1, height, width).
            param["calc_cols"] (list of str): Column names for X,Y-coordinate.
            param["pitch"] (float): Length per pixel.
            param["index_cols"] (list of str): Column names to keep in the
                result table.

        Returns:
            pandas.DataFrame: Table containing mask value column
        """
        df = reqs[0].copy()
        img = reqs[1].copy()
        if img.shape[0] > 1:
            raise Exception("Image must be split into single frames.")
        frm = img[0, :, :]
        x = df[param["calc_cols"][0]].values / param["pitch"]
        y = df[param["calc_cols"][1]].values / param["pitch"]
        x_pos = np.floor(x).astype("int")
        y_pos = np.floor(y).astype("int")
        vals = []
        for x, y in zip(x_pos, y_pos):
            if (x < 0) or (frm.shape[1] <= x) or (y < 0) or \
                    (frm.shape[0] <= y):
                vals.append(0)
            else:
                vals.append(frm[y, x])
        df["mask_val"] = vals
        use_cols = param["index_cols"] + ["mask_val"]
        del_cols = [col for col in list(df.columns) if col not in use_cols]
        df = df.drop(del_cols, axis=1)
        return df


class BinaryImage(Table):
    """Select table rows that have coordinates inside the binary mask.

    .. caution::

        The mask image should be split into a single frame image. In other
        words, the shape of reqs[1] in :meth:`process` should be (1, height,
        width).

    Args:
        reqs[0] (Table): Table including X,Y-coordinate. Required param; 
            ``pitch``, ``length_unit``.
        reqs[1] (Image): Mask image to select table.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Table with rows located inside mask image
    """
    _temp_index = []

    def __init__(self, info_path=None):
        super().__init__(info_path)
        BinaryImage._temp_index = []

    def set_reqs(self, reqs, param):
        """Drop elements that exist only in one required data.
        """
        self.reqs = setreqs.and_2reqs(reqs)

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params from reqs[1].
        """
        self.info.copy_req(0)
        self.info.copy_req(1, "param")
        length_unit = self.info.get_param_value("length_unit")
        calc_cols = ["x_" + length_unit, "y_" + length_unit]
        self.info.add_param(
            "calc_cols", calc_cols, "list of str",
            "Columns for X,Y-coordinate")
        index_cols = self.info.get_column_name("index")
        self.info.add_param("index_cols", index_cols, "list of str",
                            "Columns for index")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Select table rows that have coordinates inside the binary mask.

        Args:
            reqs[0] (pandas.DataFrame): Table including X,Y-coordinate.
            reqs[1] (numpy.ndarray): Numpy 3D array with the shape of
                (1, height, width).
            param["calc_cols"] (list of str): Column names for X,Y-coordinate.
            param["pitch"] (float): Length per pixel.

        Returns:
            pandas.DataFrame: Table rows located inside mask image
        """
        df = reqs[0].copy()
        img = reqs[1].copy()
        frm = img[0, :, :]
        x = df[param["calc_cols"][0]].values / param["pitch"]
        y = df[param["calc_cols"][1]].values / param["pitch"]
        x_pos = np.floor(x).astype("int")
        y_pos = np.floor(y).astype("int")
        vals = []
        for x, y in zip(x_pos, y_pos):
            if (x < 0) or (frm.shape[1] <= x) or \
                    (y < 0) or (frm.shape[0] <= y):
                vals.append(0)
            else:
                vals.append(frm[y, x])
        df["mask_val"] = vals

        df_index = df[param["index_cols"]].drop_duplicates()
        if len(df_index) < len(df):
            BinaryImage._temp_index.append(df_index)
        else:
            df_index = df[param["index_cols"] + ["mask_val"]]
            BinaryImage._temp_index.append(df_index)
        df = df[df["mask_val"] > 0]
        return df.drop(["mask_val"], axis=1)

    def set_index(self):
        """Set the index based on the saved temporal index.

        The file number should be added to the masked index not to skip the
        file number that is not selected.

        """
        self.info.index = pd.concat(BinaryImage._temp_index)
        self.info.set_index_file_no()
        if "mask_val" in self.info.index.columns:
            self.info.index = self.info.index[self.info.index["mask_val"] > 0]
            self.info.index = self.info.index.drop(columns=["mask_val"])
