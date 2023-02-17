import numpy as np
import pandas as pd

from ..tbl.table import Table
from .. import RANDOM_SEED
from ..fun.misc import reduce_list as rl

np.random.seed(RANDOM_SEED)


class UniformRect(Table):
    """Uniform distribution inside rectangle region.

    Args:
        reqs[0] (Index): Index Table class.
        param["pitch"] (float): Length per pixel.
        param["n_point"] (int): Number of points in one frame.
        param["lims"] (list of list of float): List of [lower, upper] limit for
            each dimension in length_unit.
        param["split_depth"] (int): File split depth number.
        param["length_unit"] (str): Unit string for column names such as "um",
            "nm".
        param["dimension"] (int): Position dimension 1=x, 2=xy, 3=xyz.
        param["seed"] (int, optional): Random seed.

    Returns:
        Table: Expanded Table including point number and coordinates
    """

    def set_info(self, param):
        self.info.copy_req()
        self.info.add_column(None, "pt_no", "int32", "num", "Point number")

        self.info.add_param("length_unit", param["length_unit"],
                            "str", "Unit of length")
        self.info.add_param("pitch", param["pitch"], param["length_unit"]
                            + "/pix", "Length per pixel")

        dims = ["x", "y", "z"]
        calc_cols = []
        for i in range(param["dimension"]):
            self.info.add_column(
                0, dims[i] + "_" + param["length_unit"], "float32",
                param["length_unit"], dims[i] + "-coordinate")
            calc_cols.append(dims[i] + "_" + param["length_unit"])
        self.info.add_param("calc_cols", calc_cols,
                            "str", "Calculation column names")
        if "seed" in param:
            self.info.add_param("seed", param["seed"], "int", "Random seed")
            np.random.seed(param["seed"])
        self.info.add_param("n_point", param["n_point"], "count",
                            "Number of points in one frame")
        self.info.add_param("lims", param["lims"],
                            "list of float",
                            "List of [lower, upper] limit for each dimension")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Uniform distribution inside rectangle region.

        Args:
            reqs[0] (pandas.DataFrame): Index DataFrame.
            param["n_point"] (int): Number of points in one frame.
            param["lims"] (list of list of float): List of [lower, upper] limit
                for each dimension.
            param["calc_cols"] (list of str): Column name of each coordinate.

        Returns:
            pandas.DataFrame: Expanded table including point no and coordinates
        """
        df_req = reqs[0].copy()
        df_list = []
        for _, df in df_req.groupby(rl(df_req.columns.values.tolist())):
            df_cols = []
            df_cols.append(pd.DataFrame(
                range(1, param["n_point"] + 1), columns=["pt_no"]))
            for col, lims in zip(param["calc_cols"], param["lims"]):
                x0 = np.random.rand(param["n_point"]) * (lims[1] - lims[0]) \
                    + lims[0]
                df_cols.append(pd.DataFrame(x0, columns=[col]))
            df_add = pd.concat(df_cols, axis=1)
            df_index = df.reset_index(drop=True)
            index_names = df_index.columns
            df_new = pd.concat([df.reset_index(drop=True), df_add], axis=1)
            df_new = df_new.fillna(method="ffill")
            df_new[index_names] = df_new[index_names].astype(int)
            df_list.append(df_new)
        return pd.concat(df_list)
