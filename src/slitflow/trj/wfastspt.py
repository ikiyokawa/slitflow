"""
.. caution::

    This module consists of brief wrapper classes of
    `fastspt <https://gitlab.com/tjian-darzacq-lab/Spot-On-cli>`_ package.

    Wrapper classes do not cover all functionality of fastspt functions.
    Please create your custom class to use fastspt functions that are not
    provided in this module.

    Do not ask the fastspt developers any questions about the wrapper part
    that is not directly related to the fastspt package.

Please cite the following publication of the original package if you use
this module.

.. code-block:: text

    Hansen, Anders S., Maxime Woringer, Jonathan B. Grimm, Luke D. Lavis,
    Robert Tjian, and Xavier Darzacq. "Robust model-based analysis of
    single-particle tracking experiments with Spot-On." Elife 7 (2018): e33125.

Reference: `Spot-On web site <https://spoton.berkeley.edu/>`_

"""

import numpy as np
import pandas as pd
import importlib  # for fastspt

import os
import sys

from ..tbl.table import Table
from ..fun.misc import reduce_list as rl


class JumpLenDist(Table):
    """Calculate jump length distribution using fastspt package.

    See also the documentation of `compute_jump_length_distribution
    <https://gitlab.com/tjian-darzacq-lab/Spot-On-cli/-/blob/master/fastspt/fastspt.py>`_.

    .. caution::

        The distribution is calculated from all trajectories entered into the
        :meth:`process`. You have to split the required data into appropriate
        depths.

    Args:
        reqs[0] (Table): Trajectory Table. Required param; ``length_unit``,
            ``interval``. Required columns; ``frm_no``, ``x_um``, ``y_um``.
        param["trj_depth"] (int): The depth number of the "trj_no" column.
        param["CDF"] (bool, optional): Whether to use CDF. Default=False.
        param["useEntireTraj"] (bool, optional): Whether to use entire
            trajectory. Defaults to False.
        param["TimePoints"] (int, optional): Maximum step number + 1 to
            make histograms. Defaults to 8.
        param["GapsAllowed"] (int, optional): Allowed gap frames in a
            trajectory. See original document.
        param["JumpsToConsider"] (int): Jumps to Consider. See original
            document.
        param["MaxJump"] (float, optional): Maximal displacement for PDF
            in micrometer. Defaults to 1.25.
        param["BinWidth"] (float, optional): Binning size for PDF in
            micrometer. Defaults to 0.010.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Jump length distribution histogram
    """

    def set_info(self, param):
        """Copy params from reqs[0] and add columns and params.
        """
        self.info.copy_req_params(0)
        length_unit = self.info.get_param_value("length_unit")
        index_cols = self.reqs[0].info.get_column_name("index")
        index_cols = index_cols[:param["trj_depth"]]
        self.info.add_column(
            1, "is_cdf", "int32", "num", "Whether histogram is CDF")
        self.info.add_column(
            2, "dt", "int32", "num", "Time difference of jump step")
        self.info.add_column(
            0, "jump_dist", "float64", length_unit, "Jump distance")
        self.info.add_column(
            0, "prob", "float64", "none", "Probability")
        self.info.add_param(
            "calc_cols", ["x_" + length_unit, "y_" + length_unit],
            "list of str", "Calculation columns")
        self.info.add_param(
            "index_cols", index_cols, "list of str",
            "Trajectory grouping column names")

        if "CDF" not in param:
            param["CDF"] = False
        self.info.add_param(
            "CDF", param["CDF"], "bool", "Whether to use CDF or not")
        if "useEntireTraj" not in param:
            param["useEntireTraj"] = False
        self.info.add_param(
            "useEntireTraj", param["useEntireTraj"], "bool",
            "Whether to use entire trajectory or not")
        if "TimePoints" not in param:
            param["TimePoints"] = 8
        self.info.add_param(
            "TimePoints", param["TimePoints"], "int",
            "Maximum step number + 1 to make histograms")
        if "GapsAllowed" not in param:
            param["GapsAllowed"] = 1
        self.info.add_param(
            "GapsAllowed", param["GapsAllowed"], "int",
            "Allowed gap frames in a trajectory")
        if "JumpsToConsider" not in param:
            param["JumpsToConsider"] = 4
        self.info.add_param(
            "JumpsToConsider", param["JumpsToConsider"], "int",
            "Jumps to Consider")
        if not param["CDF"]:
            if "MaxJump" not in param:
                param["MaxJump"] = 1.25
            self.info.add_param(
                "MaxJump", param["MaxJump"], "float",
                "Maximal displacement for PDF in micrometer")
            if "BinWidth" not in param:
                param["BinWidth"] = 0.010
            self.info.add_param(
                "BinWidth", param["BinWidth"], "float",
                "Binning size for PDF in micrometer")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Calculate jump length distribution using fastspt package.

        Args:
            reqs[0] (pandas.DataFrame): Trajectory table. Required params;
                ``length_unit``. Required columns; ``frm_no``, ``x_um`` and
                ``y_um``.
            param["index_cols"] (list of str): Trajectory grouping column
                names. Required columns; ``frm_no``.
            param["calc_cols"] (list of str): Column names of X,Y-coordinate.
            param["CDF"] (bool): Whether to use CDF. Defaults to False.
            param["useEntireTraj"] (bool): Whether to use entire trajectory.
                Defaults to False.
            param["TimePoints"] (int): Maximum step number + 1 to
                make histograms. Defaults to 8.
            param["GapsAllowed"] (int): Allowed gap frames in a
                trajectory. See original document.
            param["JumpsToConsider"] (int): Jumps to Consider. See original
                document.
            param["MaxJump"] (float): Maximal displacement for PDF
                in micrometer.
            param["BinWidth"] (float): Binning size for PDF in micrometer.

        Returns:
            pandas.DataFrame: Jump length distribution table
        """
        fastspt = importlib.import_module("fastspt")
        df = reqs[0].copy()
        cells = to_fastspt_cell(df, param)
        sys.stdout = open(os.devnull, 'w')  # suppress print()
        if param["CDF"]:
            h1 = fastspt.compute_jump_length_distribution(
                cells, CDF=param["CDF"], useEntireTraj=param["useEntireTraj"],
                TimePoints=param["TimePoints"],
                GapsAllowed=param["GapsAllowed"],
                JumpsToConsider=param["JumpsToConsider"])
            HistVecJumps = h1[2]
            JumpProb = h1[3]
            HistVecJumpsCDF = h1[0]
            JumpProbCDF = h1[1]
        else:
            h1 = fastspt.compute_jump_length_distribution(
                cells, CDF=param["CDF"], useEntireTraj=param["useEntireTraj"],
                TimePoints=param["TimePoints"],
                GapsAllowed=param["GapsAllowed"],
                JumpsToConsider=param["JumpsToConsider"],
                MaxJump=param["MaxJump"], BinWidth=param["BinWidth"])
            HistVecJumps = h1[0]
            JumpProb = h1[1]
            HistVecJumpsCDF = h1[0]
            JumpProbCDF = h1[1]
        sys.stdout = sys.__stdout__
        return to_hist_df(HistVecJumps, JumpProb, HistVecJumpsCDF, JumpProbCDF)


def to_fastspt_cell(df, param):
    """Convert trajectory table to fastspt compatible list.

    Args:
        df (pandas.DataFrame): Trajectory table containing X,Y-coordinate.
        param["index_cols"] (list of str): Column names for grouping
            trajectories. Required columns; ``frm_no``.
        param["calc_cols"] (list of str): Column names of X,Y-coordinate.
        param["interval"] (float): Time interval in second.

    Returns:
        list: fastspt compatible (xy, time, frame number) list
    """
    cells = []
    for _, row in df.groupby(rl(param["index_cols"])):
        xy = row[param["calc_cols"]].values
        frm_no = np.atleast_2d(row["frm_no"].values)
        time = frm_no * param["interval"]
        cells.append((xy, time, frm_no))
    return cells


def to_hist_df(HistVecJumps, JumpProb, HistVecJumpsCDF, JumpProbCDF):
    """Convert fastspt compatible list to :class:`pandas.DataFrame`.

    Args:
        HistVecJumps (numpy.ndarray): Jump histograms vector.
        JumpProb (numpy.ndarray): Jump probability.
        HistVecJumpsCDF (numpy.ndarray): CDF of jump histogram vector.
        JumpProbCDF (numpy.ndarray): CDF of jump probability.

    Returns:
        pandas.DataFrame: Jump length distribution histogram table
    """
    dt = []
    r = []
    prob = []
    is_cdf = []
    for i, jump in enumerate(JumpProb):
        is_cdf.append(np.full(len(jump), 0))
        dt.append(np.full(len(jump), i + 1))
        r.append(HistVecJumps)
        prob.append(jump)
    for i, jump_cdf in enumerate(JumpProbCDF):
        is_cdf.append(np.full(len(jump_cdf), 1))
        dt.append(np.full(len(jump_cdf), i + 1))
        r.append(HistVecJumpsCDF)
        prob.append(jump_cdf)
    return pd.DataFrame({"is_cdf": np.concatenate(is_cdf),
                        "dt": np.concatenate(dt),
                         "jump_dist": np.concatenate(r),
                         "prob": np.concatenate(prob)})


class FitJumpLenDist2comp(Table):
    """Fit jump length distribution to two-states model using fastspt.

    Wrapping class of `fit_jump_length_distribution
    <https://gitlab.com/tjian-darzacq-lab/Spot-On-cli/-/blob/master/fastspt/fastspt.py>`_.


    Args:
        reqs[0] (JumpLenDist): Jump length distribution Table. Required param;
            ``length_unit``, ``interval``, ``CDF``.
        param["lower_bound"] (list of float): Lower bound of fit
            parameters. The list should be [D_free, D_bound, F_bound].
        param["upper_bound"] (list of float): Upper bound of fit
            parameters. The list should be [D_free, D_bound, F_bound].
        param["LocError"] (float or list of float): Explicit localization
            error if you do not want to fit it. Otherwise [lower bound, upper
            bound] of the LocError value for fitting.
        param["iterations"] (int): Fitting iteration number.
        param["dZ"] (int): Axial illumination slice length.
        param["useZcorr"] (bool): Whether to use Z correction.
        param["a"] (float, optional): Zcorr constant a if Zcorr is used.
        param["b"] (float, optional): Zcorr constant b if Zcorr is used.
        param["init"] (list of float, optional): Initial values of fit
            parameters for [D_free, D_bound, F_bound, sigma(optional)].
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Fitting result of jump length distribution histogram
    """

    def set_info(self, param):
        """Copy params from reqs[0] and add columns.
        """
        self.info.copy_req_params(0)
        length_unit = self.info.get_param_value("length_unit")
        self.info.add_column(
            0, "d_bound", "float64", length_unit + "^2/s",
            "Diffusion coefficient of Bound fraction")
        self.info.add_column(
            0, "d_bound_stderr", "float64", length_unit + "^2/s",
            "Standard error of D_bound")
        self.info.add_column(
            0, "d_free", "float64", length_unit + "^2/s",
            "Diffusion coefficient of Free fraction")
        self.info.add_column(
            0, "d_free_stderr", "float64", length_unit + "^2/s",
            "Standard error of D_bound")
        self.info.add_column(
            0, "f_bound", "float64", "none", "Fraction of Bound fraction")
        self.info.add_column(
            0, "f_bound_stderr", "float64", "none",
            "Standard error of F_bound")
        self.info.add_column(
            0, "sigma", "float64", length_unit, "Localization error")
        self.info.add_column(
            0, "sigma_stderr", "float64", "none",
            "Standard error of localization error")
        self.info.add_param(
            "lower_bound", param["lower_bound"], "list of float",
            "The lower bound of fit parameters. [d_free, d_bound, f_bound].")
        self.info.add_param(
            "upper_bound", param["upper_bound"], "list of float",
            "The upper bound of fit parameters. [d_free, d_bound, f_bound].")
        self.info.add_param(
            "LocError", param["LocError"], "float", "Localization error")
        self.info.add_param(
            "iterations", param["iterations"], "int",
            "Fitting iteration number")
        self.info.add_param(
            "dZ", param["dZ"], "int", "Axial illumination slice length")
        self.info.add_param(
            "useZcorr", param["useZcorr"], "bool",
            "Whether to use Z correction")
        if param["useZcorr"]:
            self.info.add_param("a", param["a"], "float", "Zcorr constant a")
            self.info.add_param("b", param["b"], "float", "Zcorr constant b")
        if "init" in param:
            self.info.add_param(
                "init", param["init"], "list of float",
                "Initial parameters for fitting")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Fit jump length distribution to the model using fastspt.

        Args:
            reqs[0] (pandas.DataFrame): Jump length distribution histogram.
            param["lower_bound"] (list of float): Lower bound of fit
                parameters. The list should be [D_free, D_bound, F_bound].
            param["upper_bound"] (list of float): Upper bound of fit
                parameters. The list should be [D_free, D_bound, F_bound].
            param["LocError"] (float or list of float): Explicit localization
                error if you do not want to fit it. Otherwise [lower bound,
                upper bound] of the LocError value for fitting.
            param["iterations"] (int): Fitting iteration number.
            param["dZ"] (int): Axial illumination slice length.
            param["useZcorr"] (bool): Whether to use Z correction.
            param["a"] (float, optional): Zcorr constant a if Zcorr is used.
            param["b"] (float, optional): Zcorr constant b if Zcorr is used.
            param["init"] (list of float, optional): Initial values of fit
                parameters for [D_free, D_bound, F_bound, sigma(optional)].
            param["CDF"] (bool): Whether to use CDF.

        Returns:
            pandas.DataFrame: Fit parameters
        """
        fastspt = importlib.import_module("fastspt")
        df = reqs[0].copy()
        HistVecJumps, JumpProb, HistVecJumpsCDF, JumpProbCDF = from_hist_df(df)

        if param["CDF"]:
            ModelFit = 2
        else:
            ModelFit = 1
        if isinstance(param["LocError"], list):
            param["lower_bound"] = param["lower_bound"]\
                + [param["LocError"][0]]
            param["upper_bound"] = param["upper_bound"]\
                + [param["LocError"][1]]
            params = {"UB": param["upper_bound"], "LB": param["lower_bound"],
                      "iterations": param["iterations"], "LocError": None,
                      "dT": param["interval"], "dZ": param["dZ"],
                      "ModelFit": ModelFit, "fit2states": True,
                      "fitSigma": True,
                      "useZcorr": param["useZcorr"]}
        else:
            params = {"UB": param["upper_bound"], "LB": param["lower_bound"],
                      "LocError": param["LocError"],
                      "iterations": param["iterations"],
                      "dT": param["interval"], "dZ": param["dZ"],
                      "ModelFit": ModelFit, "fit2states": True,
                      "fitSigma": False,
                      "useZcorr": param["useZcorr"]}
        if param["useZcorr"]:
            params["a"] = param["a"]
            params["b"] = param["b"]
        else:
            params["a"] = None
            params["b"] = None
        if "init" not in param:
            init = None
        else:
            init = [np.array(param["init"])]
        sys.stdout = open(os.devnull, 'w')  # suppress print()
        fit = fastspt.fit_jump_length_distribution(
            JumpProb, JumpProbCDF, HistVecJumps, HistVecJumpsCDF,
            verbose=False, init=init, **params)
        sys.stdout = sys.__stdout__
        df = pd.DataFrame(
            {"d_bound": [fit.params["D_bound"].value],
             "d_bound_stderr": [fit.params["D_bound"].stderr],
             "d_free": [fit.params["D_free"].value],
             "d_free_stderr": [fit.params["D_free"].stderr],
             "f_bound": [fit.params["F_bound"].value],
             "f_bound_stderr": [fit.params["F_bound"].stderr],
             "sigma": [fit.params["sigma"].value],
             "sigma_stderr": [fit.params["sigma"].stderr]})
        return df


class FitJumpLenDist3comp(Table):
    """Fit jump length distribution to three-states model using fastspt.

    Wrapping class of `fit_jump_length_distribution
    <https://gitlab.com/tjian-darzacq-lab/Spot-On-cli/-/blob/master/fastspt/fastspt.py>`_.


    Args:
        reqs[0] (JumpLenDist): Jump length distribution Table. Required param;
            ``length_unit``, ``interval``, ``CDF``.
        param["lower_bound"] (list of float): Lower bound of fit
            parameters. The list should be [D_fast, D_med, D_bound, F_bound,
            F_fast] for three-states.
        param["upper_bound"] (list of float): Upper bound of fit
            parameters. The list should be [D_fast, D_med, D_bound, F_bound,
            F_fast] for three-states.
        param["LocError"] (float or list of float): Explicit localization
            error if you do not want to fit it. Otherwise [lower bound, upper
            bound] of the LocError value for fitting.
        param["iterations"] (int): Fitting iteration number.
        param["dZ"] (int): Axial illumination slice length.
        param["useZcorr"] (bool): Whether to use Z correction.
        param["a"] (float, optional): Zcorr constant a if Zcorr is used.
        param["b"] (float, optional): Zcorr constant b if Zcorr is used.
        param["init"] (list of float, optional): Initial values of fit
            parameters for [D_fast, D_med, D_bound, F_bound, sigma(optional)].
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Fitting result of jump length distribution histogram
    """

    def set_info(self, param):
        """Copy params from reqs[0] and add columns.
        """
        self.info.copy_req_params(0)
        length_unit = self.info.get_param_value("length_unit")

        self.info.add_column(
            0, "d_bound", "float64", length_unit + "^2/s",
            "Diffusion coefficient of Bound fraction")
        self.info.add_column(
            0, "d_bound_stderr", "float64", length_unit + "^2/s",
            "Standard error of D_bound")
        self.info.add_column(
            0, "d_med", "float64", length_unit + "^2/s",
            "Diffusion coefficient of Medium fraction")
        self.info.add_column(
            0, "d_med_stderr", "float64", length_unit + "^2/s",
            "Standard error of D_med")
        self.info.add_column(
            0, "d_fast", "float64", length_unit + "^2/s",
            "Diffusion coefficient of Fast fraction")
        self.info.add_column(
            0, "d_fast_stderr", "float64", length_unit + "^2/s",
            "Standard error of D_fast")
        self.info.add_column(
            0, "f_bound", "float64", "none", "Fraction of Bound fraction")
        self.info.add_column(
            0, "f_bound_stderr", "float64", "none",
            "Standard error of F_bound")
        self.info.add_column(
            0, "f_fast", "float64", "none", "Fraction of Fast fraction")
        self.info.add_column(
            0, "f_fast_stderr", "float64", "none",
            "Standard error of F_fast")
        self.info.add_column(
            0, "sigma", "float64", length_unit, "Localization error")
        self.info.add_column(
            0, "sigma_stderr", "float64", "none",
            "Standard error of localization error")
        self.info.add_param(
            "lower_bound", param["lower_bound"], "list of float",
            "Lower bound of fit parameters. [d_fast, d_med, d_bound,\
             f_bound, f_fast].")
        self.info.add_param(
            "upper_bound", param["upper_bound"], "list of float",
            "Upper bound of fit parameters. [d_fast, d_med, d_bound,\
             f_bound, f_fast].")
        self.info.add_param(
            "LocError", param["LocError"], "float", "Localization error")
        self.info.add_param(
            "iterations", param["iterations"], "int",
            "Fitting iteration number")
        self.info.add_param(
            "dZ", param["dZ"], "int", "Axial illumination slice length")
        self.info.add_param(
            "useZcorr", param["useZcorr"], "bool",
            "Whether to use Z correction")
        if param["useZcorr"]:
            self.info.add_param("a", param["a"], "float", "Zcorr constant a")
            self.info.add_param("b", param["b"], "float", "Zcorr constant b")

        if "init" in param:
            self.info.add_param(
                "init", param["init"], "list of float",
                "Initial parameters for fitting")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Fit jump length distribution to the three-states model by fastspt.

        Args:
            reqs[0] (pandas.DataFrame): Jump length distribution histogram.
            param["lower_bound"] (list of float): Lower bound of fit
                parameters. The list should be [D_fast, D_med, D_bound,
                F_bound, F_fast] for three-states.
            param["upper_bound"] (list of float): Upper bound of fit
                parameters. The list should be [D_fast, D_med, D_bound,
                F_bound, F_fast] for three-states.
            param["LocError"] (float or list of float): Explicit localization
                error if you do not want to fit it. Otherwise [lower bound,
                upper bound] of the LocError value for fitting.
            param["iterations"] (int): Fitting iteration number.
            param["dZ"] (int): Axial illumination slice length.
            param["useZcorr"] (bool): Whether to use Z correction or not.
            param["a"] (float, optional): Zcorr constant a if Zcorr is used.
            param["b"] (float, optional): Zcorr constant b if Zcorr is used.
            param["CDF"] (bool): Whether to use CDF.
            param["init"] (list of float, optional): Initial values of fit
                parameters for [D_fast, D_med, D_bound, F_bound,
                sigma(optional)].

        Returns:
            pandas.DataFrame: Fit parameters
        """
        fastspt = importlib.import_module("fastspt")
        df = reqs[0].copy()
        HistVecJumps, JumpProb, HistVecJumpsCDF, JumpProbCDF = from_hist_df(df)
        if param["CDF"]:
            ModelFit = 2
        else:
            ModelFit = 1
        if isinstance(param["LocError"], list):
            param["lower_bound"] = param["lower_bound"]\
                + [param["LocError"][0]]
            param["upper_bound"] = param["upper_bound"]\
                + [param["LocError"][1]]
            params = {"UB": param["upper_bound"], "LB": param["lower_bound"],
                      "iterations": param["iterations"], "LocError": None,
                      "dT": param["interval"], "dZ": param["dZ"],
                      "ModelFit": ModelFit, "fit2states": False,
                      "fitSigma": True,
                      "useZcorr": param["useZcorr"]}
        else:
            params = {"UB": param["upper_bound"], "LB": param["lower_bound"],
                      "LocError": param["LocError"],
                      "iterations": param["iterations"],
                      "dT": param["interval"], "dZ": param["dZ"],
                      "ModelFit": ModelFit, "fit2states": False,
                      "fitSigma": False,
                      "useZcorr": param["useZcorr"]}
        if param["useZcorr"]:
            params["a"] = param["a"]
            params["b"] = param["b"]
        else:
            params["a"] = None
            params["b"] = None
        if "init" not in param:
            init = None
        else:
            init = [np.array(param["init"])]  # should be list of np.array
        sys.stdout = open(os.devnull, 'w')  # suppress print()
        fit = fastspt.fit_jump_length_distribution(
            JumpProb, JumpProbCDF, HistVecJumps, HistVecJumpsCDF,
            verbose=False, init=init, **params)
        sys.stdout = sys.__stdout__

        df = pd.DataFrame(
            {"d_bound": [fit.params["D_bound"].value],
             "d_bound_stderr": [fit.params["D_bound"].stderr],
             "d_med": [fit.params["D_med"].value],
             "d_med_stderr": [fit.params["D_med"].stderr],
             "d_fast": [fit.params["D_fast"].value],
             "d_fast_stderr": [fit.params["D_fast"].stderr],
             "f_bound": [fit.params["F_bound"].value],
             "f_bound_stderr": [fit.params["F_bound"].stderr],
             "f_fast": [fit.params["F_fast"].value],
             "f_fast_stderr": [fit.params["F_fast"].stderr],
             "sigma": [fit.params["sigma"].value],
             "sigma_stderr": [fit.params["sigma"].stderr]})
        return df


def from_hist_df(df):
    """Convert :class:`pandas.DataFrame` to jump length distribution.

    Args:
        df (pandas.DataFrame): Table of jump length distribution.

    Returns:
        tuple: Histograms for fitting (HistVecJumps, JumpProb, HistVecJumpsCDF,
        JumpProbCDF)
    """
    JumpProb = []
    JumpProbCDF = []
    pdf = df[df["is_cdf"] == 0]
    for i, row in pdf.groupby("dt"):
        if i == 1:
            HistVecJumps = row["jump_dist"].values
        JumpProb.append(row["prob"].values)
    JumpProb = np.vstack(JumpProb)
    cdf = df[df["is_cdf"] == 1]
    for i, row in cdf.groupby("dt"):
        if i == 1:
            HistVecJumpsCDF = row["jump_dist"].values
        JumpProbCDF.append(row["prob"].values)
    JumpProbCDF = np.vstack(JumpProbCDF)
    return HistVecJumps, JumpProb, HistVecJumpsCDF, JumpProbCDF


class ModelJumpLenDist(Table):
    """Create model curve of jump length distribution from fit parameters.

    Wrapping class of `generate_jump_length_distribution
    <https://gitlab.com/tjian-darzacq-lab/Spot-On-cli/-/blob/master/fastspt/fastspt.py>`_.

    Args:
        reqs[0] (JumpLenDist): Histogram of jump length distribution. Required
            params; ``length_unit``.
        reqs[1] (FitJumpLenDist2comp or FitJumpLenDist3comp) : Fitting
            parameters of two or three-states model.
        param["show_pdf"] (bool): Whether to use the PDF model.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Jump length distribution histogram model
    """

    def set_info(self, param):
        """Copy params from reqs[0] and reqs[1] then add columns.
        """
        self.info.copy_req_params(0)
        self.info.copy_req_params(1)
        length_unit = self.info.get_param_value("length_unit")
        self.info.add_column(
            1, "is_cdf", "int32", "num", "Whether histogram is CDF")
        self.info.add_column(
            2, "dt", "int32", "num", "Time difference of jump step")
        self.info.add_column(
            0, "jump_dist", "float64", length_unit, "Jump distance")
        self.info.add_column(
            0, "prob", "float64", "none", "Probability")
        self.info.add_param(
            "show_pdf", param["show_pdf"], "bool",
            "Whether to use the PDF model")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Create model curve of jump length distribution from fit params.

        Args:
            reqs[0] (JumpLenDist): Histogram of jump length distribution.
                Required params; ``length_unit``.
            reqs[1] (FitJumpLenDist2comp or FitJumpLenDist3comp) : Fitting
                parameters of two or three-states model.
            param["show_pdf"] (bool) : Whether to use the PDF model.
            param["CDF"] (bool): Whether to use CDF.
            param["dZ"] (int): Axial illumination slice length.
            param["useZcorr"] (bool): Whether to use Z correction.
            param["a"] (float, optional): Zcorr constant a if Zcorr is used.
            param["b"] (float, optional): Zcorr constant b if Zcorr is used.
            param["interval"] (float): Time interval.

        Returns:
            pandas.DataFrame: Jump length distribution histogram model
        """
        fastspt = importlib.import_module("fastspt")
        df_hist = reqs[0].copy()
        df_fit = reqs[1].copy()

        HistVecJumps, JumpProb, HistVecJumpsCDF, JumpProbCDF = \
            from_hist_df(df_hist)

        if len(df_fit.columns) == 8:  # Two-states model
            fitparams = {"D_free": df_fit.d_free[0],
                         "D_bound": df_fit.d_bound[0],
                         "F_bound": df_fit.f_bound[0]}
            fit2states = True
        else:  # Three-states model
            fitparams = {"D_bound": df_fit.d_bound[0],
                         "D_med": df_fit.d_med[0],
                         "D_fast": df_fit.d_fast[0],
                         "F_bound": df_fit.f_bound[0],
                         "F_fast": df_fit.f_fast[0]}
            fit2states = False
        if param["show_pdf"]:
            HistVec = HistVecJumps
            Prob = JumpProb
        else:
            if not param["CDF"]:
                raise Exception("CDF is not calculated.")
            HistVec = HistVecJumpsCDF
            Prob = JumpProbCDF
        if not param["useZcorr"]:
            param["a"] = None
            param["b"] = None
        y = fastspt.generate_jump_length_distribution(
            fitparams, JumpProb=Prob, r=HistVec, fit2states=fit2states,
            LocError=df_fit.sigma[0], dT=param['interval'], dZ=param['dZ'],
            a=param['a'], b=param['b'], norm=True,
            useZcorr=param['useZcorr'])

        df = to_model_hist_df(HistVec, y)
        df["is_cdf"] = int(not param["show_pdf"])
        df = df[df_hist.columns]
        return df


def to_model_hist_df(HistVec, y):
    """Convert jump length distribution histogram model to
    :class:`pandas.DataFrame`.

    Args:
        HistVec (numpy.ndarray): X-axis of jump length distribution.
        y (numpy.ndarray): Jump length distribution histogram model.

    Returns:
        pandas.DataFrame: Jump length distribution histogram model
    """
    dt = []
    r = []
    prob = []
    for i, jump_cdf in enumerate(y):
        dt.append(np.full(len(jump_cdf), i + 1))
        r.append(HistVec)
        prob.append(jump_cdf)
    return pd.DataFrame({"dt": np.concatenate(dt),
                         "jump_dist": np.concatenate(r),
                         "prob": np.concatenate(prob)})
