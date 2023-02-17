import numpy as np
import pandas as pd
from scipy.spatial import distance

from ..tbl.table import Table
from .. import RANDOM_SEED
from ..fun.misc import reduce_list as rl

np.random.seed(RANDOM_SEED)


class Walk2DCenter(Table):
    """Create X,Y-coordinate of two-dimensional random walk.

    Trajectories are assumed starting from (0,0).

    Args:
        reqs[0] (Index): Index Table class.
        param["length_unit"] (str): String of length unit such as "um",
            "nm", "pix". This string is used as column name footers and units.
        param["diff_coeff"] (float): Diffusion coefficient in length_unit^2/s.
        param["interval"] (int): Time interval in second.
        param["n_step"] (int): Step number of trajectory. e.g. n_step=3 
            contains four points.
        param["seed"] (int, optional): Random seed.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Expanded Table including frame number and coordinates

    Examples:
        Add three-step trajectories to the Index table.

        .. code-block:: python

            D1 = sf.tbl.create.Index()
            D1.run([],{"type":"trajectory", "index_counts":[2,3], "split_depth":0})

            D2 = sf.trj.random.Walk2DCenter()
            D2.run([D1],{"length_unit": "um", "diff_coeff": 0.1, "interval": 0.1,
                        "n_step":3, "seed": 1,  "split_depth":0})
            print(D2.data[0])
            #     img_no  trj_no  frm_no      x_um      y_um
            # 0        1       1       1  0.000000  0.000000
            # 1        1       1       2  0.229717 -0.151741
            # 2        1       1       3  0.143202 -0.029354
            # 3        1       1       4  0.068507 -0.354840
            # 4        1       2       1  0.000000  0.000000
            # 5        1       2       2  0.246754 -0.035266
            # ...
            # 22       2       3       3 -0.153925 -0.214459
            # 23       2       3       4 -0.251106 -0.216250
    """

    def set_info(self, param):
        """Copy info from reqs[0] and add columns and params.
        """
        self.info.copy_req(0)
        self.info.add_column(
            None, "frm_no", "int32", "num", "Frame number")
        self.info.add_column(
            0, "x_" + param["length_unit"], "float64", param["length_unit"],
            "X-coordinate")
        self.info.add_column(
            0, "y_" + param["length_unit"], "float64", param["length_unit"],
            "Y-coordinate")
        self.info.add_param(
            "diff_coeff", param["diff_coeff"], param["length_unit"] + "^2/s",
            "Diffusion coefficient")
        self.info.add_param(
            "interval", param["interval"], "s", "Time interval")
        if "seed" in param:
            self.info.add_param("seed", param["seed"], "int", "Random seed")
            np.random.seed(param["seed"])
        self.info.add_param(
            "n_step", param["n_step"], "num", "Step number of trajectory")
        self.info.add_param(
            "calc_cols", ["x_" + param["length_unit"],
                          "y_" + param["length_unit"]],
            "list of str", "Random walk calc column names")
        self.info.add_param(
            "length_unit", param["length_unit"], "str", "Length unit")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """X,Y-coordinate of two-dimensional random walk.

        Random seed should be set before running this function.

        Args:
            reqs[0] (pandas.DataFrame): Index DataFrame.
            param["diff_coeff"] (float): Diffusion coefficient.
            param["interval"] (int): Time interval.
            param["n_step"] (int): Step number of trajectory.
            param["calc_cols"] (list of str): Column name of each coordinate.

        Returns:
            pandas.DataFrame: Expanded table including frame number and
            coordinates
        """
        dfs_req = reqs[0].copy()
        df_list = []
        for _, df in dfs_req.groupby(rl(dfs_req.columns.values.tolist())):
            df_cols = []
            df_cols.append(pd.DataFrame(
                range(1, param["n_step"] + 2), columns=["frm_no"]))
            for col in param["calc_cols"]:
                dx = np.sqrt(2 * param["diff_coeff"] * param["interval"]) * \
                    np.random.randn(param["n_step"])
                value = np.append(0, np.cumsum(dx))
                df_cols.append(pd.DataFrame(value, columns=[col]))
            df_add = pd.concat(df_cols, axis=1)
            df_index = df.reset_index(drop=True)
            index_names = df_index.columns
            df_new = pd.concat([df.reset_index(drop=True), df_add], axis=1)
            df_new = df_new.fillna(method="ffill")
            df_new[index_names] = df_new[index_names].astype(int)
            df_list.append(df_new)
        return pd.concat(df_list)


class WalkRect(Table):
    """Random walk with a rectangle barrier.

    Trajectories are assumed starting from the random position.

    Args:
        reqs[0] (Index): Index Table class.
        param["dimension"] (int): Position dimension. 1=x, 2=xy, 3 = xyz.
        param["length_unit"] (str): String of length unit such as "um",
            "nm", "pix". This string is used as column name footers and units.
        param["diff_coeff"] (float): Diffusion coefficient in length_unit^2/s.
        param["interval"] (int): Time interval in second.
        param["n_step"] (int): Step number of trajectory. n_step=3 contains
            four points.
        param["lims"] (list of list of float): List of [lower, upper]
            localization limits for each dimension.
        param["seed"] (int, optional): Random seed.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Expanded Table including frame number and coordinates

    Examples:
        Add three-step trajectories into the Index table.

        .. code-block:: python

            D1 = sf.tbl.create.Index()
            D1.run([],{"type":"trajectory", "index_counts":[2,3], "split_depth":0})

            D2 = sf.trj.random.WalkRect()
            D2.run([D1],{"dimension":2, "length_unit": "um", "diff_coeff": 0.1, 
                        "interval": 0.1, "n_step":3, "lims": [[0, 1], [0, 1]],
                        "seed": 1,  "split_depth":0})
            print(D2.data[0])
            #     img_no  trj_no  frm_no      x_um      y_um
            # 0        1       1       1  0.396767  0.685220
            # 1        1       1       2  0.626485  0.533479
            # 2        1       1       3  0.539969  0.199234
            # 3        1       1       4  0.465274  0.359796
            # 4        1       2       1  0.140387  0.968262
            # 5        1       2       2  0.185506  0.676914
            # ...
            # 21       2       3       2  0.929132  0.410367
            # 22       2       3       3  0.824191  0.328230
            # 23       2       3       4  0.797061  0.312567
    """

    def set_info(self, param):
        self.info.copy_req(0)
        self.info.add_column(None, "frm_no", "int32", "num", "Frame number")

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
            self.info.add_param(
                "seed", param["seed"], "int", "Random seed")
            np.random.seed(param["seed"])
        self.info.add_param(
            "diff_coeff", param["diff_coeff"], param["length_unit"] + "^2/s",
            "Diffusion coefficient")
        self.info.add_param(
            "interval", param["interval"], "s", "Time interval")
        self.info.add_param(
            "n_step", param["n_step"], "num", "Step number of trajectory")
        self.info.add_param(
            "lims", param["lims"], "list of float",
            "[lower, upper] limit of each columns")
        self.info.add_param(
            "length_unit", param["length_unit"], "str", "Unit of length")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Add random walk coordinates to index DataFrame.

        Random seed should be set before run this function.

        Args:
            reqs[0] (pandas.DataFrame): Index DataFrame.
            param["diff_coeff"] (float): Diffusion coefficient.
            param["interval"] (int): Time interval in second.
            param["n_step"] (int): Step number of trajectory.
            param["calc_cols"] (list of str): Column name of each coordinate.
            param["lims"] (list of list of float): List of [lower, upper]
                localization limits for each dimension.

        Returns:
            pandas.DataFrame: Expanded table including frame number and
            coordinates
        """
        dfs_req = reqs[0].copy()
        df_list = []
        for _, df in dfs_req.groupby(rl(dfs_req.columns.values.tolist())):
            df_cols = []
            df_cols.append(pd.DataFrame(
                range(1, param["n_step"] + 2), columns=["frm_no"]))
            for col, lims in zip(param["calc_cols"], param["lims"]):
                dxs = np.sqrt(2 * param["diff_coeff"] * param["interval"]) \
                    * np.random.randn(param["n_step"])
                x0 = np.random.rand(1) * (lims[1] - lims[0]) + lims[0]
                value = reflect_in_rect(x0, dxs, lims)
                df_cols.append(pd.DataFrame(value, columns=[col]))
            df_add = pd.concat(df_cols, axis=1)
            df_index = df.reset_index(drop=True)
            index_names = df_index.columns
            df_new = pd.concat([df.reset_index(drop=True), df_add], axis=1)
            df_new = df_new.fillna(method="ffill")
            df_new[index_names] = df_new[index_names].astype(int)
            df_list.append(df_new)
        return pd.concat(df_list)


def reflect_in_rect(x0, dxs, lims):
    """Reflect displacements if next position is outside the limits.

    Args:
        x0 (float): One-dimensional coordinate of particle start position.
        dxs (list of float): List of one-dimensional displacements.
        lims (list of float): [lower, upper] of border positions to reflect.

    Returns:
        numpy.ndarray: List of one-dimensional positions to which the
        reflection is applied
    """
    lower, upper = lims
    x = np.array(x0)
    for dx in dxs:
        if x[-1] + dx > upper:
            x = np.append(x, x[-1] - dx)
        elif x[-1] + dx < lower:
            x = np.append(x, x[-1] - dx)
        else:
            x = np.append(x, x[-1] + dx)
    return x


class WalkCircle(Table):
    """Random walk with a circular barrier.

    Trajectories are assumed starting from the random position.

    Args:
        reqs[0] (Index): Index Table class.
        param["dimension"] (int): Position dimension. 1=x, 2=xy, 3 = xyz.
        param["length_unit"] (str): String of length unit such as "um",
            "nm", "pix". This string is used as column name footers and units.
        param["diff_coeff"] (float): Diffusion coefficient in length_unit^2/s.
        param["interval"] (int): Time interval in second.
        param["n_step"] (int): Step number of trajectory. n_step=3 contains
            four points.
        param["radius"] (float): Radius of circular diffusion barrier.
        param["offset"] (list of float, optional): [x, y, (z)] position of the
            circle center. Defaults to [0, 0].
        param["seed"] (int, optional): Random seed.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Expanded Table including frame number and coordinates
    """

    def set_info(self, param):
        self.info.copy_req(0)
        self.info.add_column(None, "frm_no", "int32", "num", "Frame number")

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
            self.info.add_param(
                "seed", param["seed"], "int", "Random seed")
            np.random.seed(param["seed"])
        self.info.add_param(
            "diff_coeff", param["diff_coeff"], param["length_unit"] + "^2/s",
            "Diffusion coefficient")
        self.info.add_param(
            "interval", param["interval"], "s", "Time interval")
        self.info.add_param(
            "n_step", param["n_step"], "num", "Step number of trajectory")
        self.info.add_param(
            "radius", param["radius"], "float",
            "Radius of circular diffusion barrier")
        self.info.add_param(
            "offset", param["offset"], "float",
            "[x, y, (z)] position of the circle center.")
        self.info.add_param(
            "length_unit", param["length_unit"], "str", "Unit of length")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Add random walk coordinates to index DataFrame.

        Random seed should be set before running this function.

        Args:
            reqs[0] (pandas.DataFrame): Index DataFrame.
            param["diff_coeff"] (float): Diffusion coefficient.
            param["interval"] (int): Time interval in second.
            param["n_step"] (int): Step number of trajectory.
            param["calc_cols"] (list of str): Column name of each coordinate.
            param["radius"] (float): Radius of circular diffusion barrier.
            param["offset"] (list of float, optional): [x, y, (z)] position of
                the circle center.

        Returns:
            pandas.DataFrame: Expanded table including frame number and 
            coordinates
        """
        dfs_req = reqs[0].copy()
        n_dim = len(param["calc_cols"])
        frm_no = np.arange(1, param["n_step"] + 2).reshape([-1, 1])

        df_list = []
        for _, df in dfs_req.groupby(rl(dfs_req.columns.values.tolist())):
            # make initial position
            while True:
                x0 = (2 * np.random.rand(n_dim) - 1) * param["radius"]
                if distance.euclidean(x0, np.zeros(n_dim)) <= param["radius"]:
                    break
            # add diffusion steps
            xs = [x0]
            for _ in range(param["n_step"]):
                while True:
                    dx = np.sqrt(2 * param["diff_coeff"] * param["interval"]) \
                        * np.random.randn(n_dim)
                    x1 = xs[-1] + dx
                    if distance.euclidean(x1, np.zeros(n_dim)) <= \
                            param["radius"]:
                        break
                xs.append(x1)
            xs = np.array(xs) + np.array(param["offset"])
            # make data frame
            df_add = pd.DataFrame(np.concatenate([frm_no, xs], 1),
                                  columns=["frm_no"] + param["calc_cols"])
            df_index = df.reset_index(drop=True)
            index_names = list(df_index.columns) + ["frm_no"]
            df_new = pd.concat([df.reset_index(drop=True), df_add], axis=1)
            df_new = df_new.fillna(method="ffill")
            df_new[index_names] = df_new[index_names].astype(int)
            df_list.append(df_new)
        return pd.concat(df_list)
