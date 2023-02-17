"""
.. caution::

    This module consists of brief wrapper classes of
    `Trackpy <http://soft-matter.github.io/trackpy>`_.

    Wrapper classes do not cover all functionality of Trackpy functions.
    Please create your custom class to use Trackpy functions that are not
    provided in this module.

    Do not ask the Trackpy developers any questions about the wrapper part
    that is not directly related to the Trackpy package.

If you use Trackpy functions in this module, please cite original package
according to `the package documentation
<http://soft-matter.github.io/trackpy/v0.5.0/introduction.html#citing-trackpy>`_.

"""
import numpy as np
import pandas as pd
import importlib
# trackpy  # visual studio 2008 c++ runtime required
# numba 0.55.2 requires numpy<1.23,>=1.18
from tqdm import tqdm
from ..tbl.table import Table, merge_overlap_index
from .. import setindex


class Link(Table):
    """Brief wrapper of trackpy link function.

    See also `trackpy.link <http://soft-matter.github.io/trackpy/v0.5.0/generated/trackpy.link.html#trackpy.link>`_
    function. While trackpy supports 3D, this wrapper class uses only 2D image.

    The input localization table should have all frames for linking. You have
    to split data into appropriate depths. Currently, only the table containing
    ``img_no``, ``frm_no``, ``x_(length_unit)`` and ``y_(length_unit)`` is
    available.

    Args:
        reqs[0] (Table): X,Y-coordinate of localization. Required params;
            ``length_unit``. Required columns; ``img_no``, ``frm_no``,
            ``x_(length_unit)`` and ``y_(length_unit)``.
        param["search_range"] (float): Maximum distance features can move
            between frames in length_unit.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Trajectory Table
    """

    def set_info(self, param):
        """Copy info from reqs[0] and add params.

        .. caution::

            Currently, only the table containing ``img_no``, ``frm_no``,
            ``x_(length_unit)`` and ``y_(length_unit)`` is available.

        """
        self.info.copy_req(0)
        length_unit = self.info.get_param_value("length_unit")
        self.info.add_column(
            2, "trj_no", "int32", "num", "Trajectory number")
        self.info.delete_column(
            keeps=["img_no", "trj_no", "frm_no",
                   "x_" + length_unit, "y_" + length_unit])
        calc_cols = ["x_" + length_unit, "y_" + length_unit]
        self.info.add_param(
            "calc_cols", calc_cols, "list of str",
            "Column names of X,Y-coordinate")
        all_cols = self.info.get_column_name("all")
        self.info.add_param(
            "all_cols", all_cols, "list of str", "Columns for reindex")
        index_cols = self.info.get_column_name("index")
        self.info.add_param(
            "index_cols", index_cols, "list of str", "Columns for index")
        self.info.add_param(
            "search_range", param["search_range"], length_unit,
            "Maximum distance features which can move between frames")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Brief wrapper of trackpy link function.

        Args:
            reqs[0] (pandas.DataFrame): X,Y-coordinate of localization.
                Required params; ``length_unit``. Required columns; ``img_no``,
                ``frm_no``, ``x_(length_unit)`` and ``y_(length_unit)``.
            param["search_range"] (float): Maximum distance features
                can move between frames in length_unit.
            param["calc_cols"] (list of str): Column names of X,Y-coordinate.
            param["all_cols"] (list of str): Column names for reindex.
            param["index_cols"] (list of str): Column names for index.

        Returns:
            pandas.DataFrame: Trajectory table
        """
        tp = importlib.import_module("trackpy")
        df = reqs[0].copy()
        tp.quiet()
        df_track = tp.link(
            df, param["search_range"], pos_columns=param["calc_cols"],
            t_column="frm_no")
        df_track = df_track.rename(columns={"particle": "trj_no"})
        df_track["trj_no"] = df_track["trj_no"] + 1
        df_track = df_track.reindex(columns=param["all_cols"])
        df_track = df_track.sort_values(param["index_cols"])
        return df_track


class RefineCoM(Table):
    """Refine localization using center of mass in trackpy.

    Args:
        reqs[0] (Image): Raw movie Image. Required parameters; ``length_unit``,
            ``img_size``.
        reqs[1] (Table): X,Y-coordinate of trajectory. Required columns;
            ``x_(length_unit)``, ``y_(length_unit)``.
        param["radius"] (int): Mask radius for trackpy.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Refined X,Y-coordinate
    """

    def set_info(self, param):
        """Copy info from reqs[1] and param from reqs[0] and modify and
        add params.

        """
        self.info.copy_req(1)
        self.info.copy_req_params(0)
        length_unit = self.info.get_param_value("length_unit")
        self.info.add_column(
            0, "intensity", "float64", "a.u.", "Total intensity (mass)")
        self.info.add_param(
            "calc_cols", ["x_" + length_unit, "y_" + length_unit],
            "list of str", "Calculation Columns")
        self.info.add_param(
            "radius", param["radius"], "num", "Mask radius for trackpy")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Refine localization using center of mass in trackpy.

        Args:
            reqs[0] (numpy.ndarray): Raw movie Image.
            reqs[1] (pandas.DataFrame): X,Y-coordinate of trajectory. Required
                columns; ``x_(length_unit)``, ``y_(length_unit)``.
            param["img_size"] (list of int): [width, height] of each image in
                pixel.
            param["pitch"] (float): Pixel size in length_unit/pix.
            param["radius"] (int): Mask radius for trackpy in pixel.
            param["calc_cols"] (list of str): Column names for [x, y]
                coordinates.

        Returns:
            pandas.DataFrame: Refined X,Y-coordinate
        """
        tp = importlib.import_module("trackpy")
        img = reqs[0].copy()
        df = reqs[1].copy()
        width = param["img_size"][0]
        height = param["img_size"][1]
        x_col = param["calc_cols"][0]
        y_col = param["calc_cols"][1]
        r = param["radius"]
        df["x_pix"] = df[x_col] / param["pitch"]
        df["y_pix"] = df[y_col] / param["pitch"]
        # Remove outside points
        to_x = np.logical_and(r + 1 < df["x_pix"], df["x_pix"] < width - r)
        to_y = np.logical_and(r + 1 < df["y_pix"], df["y_pix"] < height - r)
        to_sel = np.logical_and(to_x, to_y)
        df = df.loc[to_sel, :]
        dfs = []
        for i in tqdm(range(img.shape[0]), leave=False):
            frm = img[i, :, :]
            df_frm = df[df["frm_no"] == i + 1]
            dfs.append(tp.refine_com(
                frm, frm, r, df_frm, pos_columns=["y_pix", "x_pix"],
                characterize=False))
        df_refine = pd.concat(dfs)
        df_refine = df_refine.rename(columns={"mass": "intensity"})
        df_refine["img_no"] = df["img_no"]
        df_refine["frm_no"] = df["frm_no"]
        df_refine["pt_no"] = df["pt_no"]
        df_refine[x_col] = df_refine["x_pix"] * param["pitch"]
        df_refine[y_col] = df_refine["y_pix"] * param["pitch"]
        df_refine = df_refine.reindex(
            columns=["img_no", "frm_no", "pt_no", x_col, y_col, "intensity"])
        return df_refine


class Locate(Table):
    """Brief wrapper of trackpy batch function.

    This class uses only two-dimensional image.
    Image stack should be split into the image number.

    Args:
        reqs[0] (Image): Image for location detection. Required
            parameters: ``length_unit``.
        param["diameter"] (odd integer): Feature size in pixel.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: X,Y-coordinate of detected points
    """

    def set_index(self):
        """Copy index from required data index and result pandas.DataFrame.
        """
        setindex.from_req_plus_data(self, 0)

    def set_info(self, param):
        """Copy information from reqs[0] and modify columns and add params.
        """
        self.info.copy_req(0)
        length_unit = self.info.get_param_value("length_unit")
        self.info.delete_column(["intensity"])
        self.info.add_column(0, "pt_no", "int", "num", "Point number")
        self.info.add_column(
            0, "x_" + length_unit, "float", length_unit,
            "X-coordinate of point")
        self.info.add_column(
            0, "y_" + length_unit, "float", length_unit,
            "Y-coordinate of point")
        self.info.add_column(
            0, "mass", "float", "a.u.",
            "Total integrated brightness of the blob")
        self.info.add_column(
            0, "size", "float", length_unit,
            "Radius of gyration of its Gaussian-like profile")
        self.info.add_column(
            0, "ecc", "float", "none",
            "Eccentricity (0 is circular)")
        self.info.add_column(0, "signal", "float", "a.u.", "Signal")
        self.info.add_column(
            0, "raw_mass", "float", "a.u.",
            "Total integrated brightness in raw_image")
        self.info.add_column(
            0, "ep", "float", length_unit,
            "Error in a feature's position")
        self.info.add_param(
            "diameter", param["diameter"],
            "pixel", "Feature size in pixel")
        self.info.add_param(
            "col_names", self.info.get_column_name("col"),
            "list of str", "Column names")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Brief wrapper of trackpy batch function.

        Args:
            reqs[0] (numpy.ndarray): Numpy 2D array of image for location
                detection.
            param["diameter"] (odd integer): Feature size in pixel.
            param["pitch"] (float): Pixel size in length_unit/pix.
            param["col_names"] (list of str): List of column names. This should
                be [frame number (frm_no), point number (point_no),
                X-coordinate (x_[length_unit]), Y-coordinate (y_[length_unit]),
                Total integrated brightness (mass), Radius of gyration (size),
                Eccentricity (ecc), Signal (signal), Total integrated
                brightness in raw_image (raw_mass), Error in a feature's
                position (ep)].

        Returns:
            pandas.DataFrame: X,Y-coordinate and other parameters of detected
            points
        """
        tp = importlib.import_module("trackpy")
        img = reqs[0].copy()
        tp.quiet()
        frames = []
        for i in range(img.shape[0]):
            frames.append(img[i, :, :])
        df = tp.batch(frames, param["diameter"])
        df["x"] = df["x"] * param["pitch"]
        df["y"] = df["y"] * param["pitch"]
        df["size"] = df["size"] * param["pitch"]
        df["ep"] = df["ep"] * param["pitch"]
        df["frame"] = df["frame"] + 1
        df["pt_no"] = df.groupby(["frame"]).cumcount() + 1
        df = df.reindex(columns=["frame", "pt_no", "x", "y", "mass", "size",
                                 "ecc", "signal", "raw_mass", "ep"])
        index = ["frm_no"] + param["col_names"]
        df = df.set_axis(index, axis='columns')
        return df

    def post_run(self):
        """Merge the index table to the split result data.
        """
        merge_overlap_index(self, 0, ["frm_no"])
