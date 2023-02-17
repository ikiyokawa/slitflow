import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.optimize import OptimizeWarning

from ..tbl.table import Table
from ..fun.misc import reduce_list as rl

import warnings
warnings.simplefilter("ignore", RuntimeWarning)


class Each(Table):
    """Mean Square Displacement of each trajectory.

    Args:
        reqs[0] (Table): Table containing X,Y-coordinate of trajectories.
            Required params; ``length_unit``, ``interval``.
            Required column; ``trj_no``, ``x_(length_unit)``,
            ``y_(length_unit)``.
        param["group_depth"] (int): Column depth number of trajectory number.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Mean square displacement with time interval

    Examples:
        Calculate MSDs of each trajectory.

        .. code-block:: python

            # D2 is from the trj.random.Walk2DCenter example
            D3 = sf.trj.msd.Each()
            D3.run([D2], {"group_depth": 2, "split_depth": 0})
            print(D3.data[0])
                  img_no  trj_no  interval       msd
            # 0        1       1       0.0  0.000000
            # 1        1       1       0.1  0.057107
            # 2        1       1       0.2  0.032046
            # 3        1       1       0.3  0.063900
            # ...
            # 33       2       3       0.3  0.146120
            # 34       2       3       0.4  0.222287
            # 35       2       3       0.5  0.310305

    """

    def set_info(self, param={}):
        """Copy info from req[0] and add columns and params.
        """
        self.info.copy_req(0)
        length_unit = self.info.get_param_value("length_unit")
        self.info.set_group_depth(param["group_depth"])
        self.info.delete_column(keeps=self.info.get_param_value("index_cols"))
        self.info.add_column(
            0, "interval", "float64", "s", "Time interval of MSD")
        self.info.add_column(
            0, "msd", "float64", length_unit + "^2",
            "Mean square displacement")
        self.info.add_param(
            "calc_cols", ["x_" + length_unit, "y_" + length_unit],
            "list of str", "MSD calculation columns")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Mean Square Displacement of each trajectory.

        Args:
            reqs[0] (pandas.DataFrame): Table containing X,Y-coordinate of
                trajectories. Required column; ``trj_no``, ``x_(length_unit)``,
                ``y_(length_unit)``.
            param["index_cols"] (list of str): Column names of index.
            param["interval"] (float): Time interval of trajectory.

        Returns:
            pandas.DataFrame: Mean square displacement with time interval
        """
        df = reqs[0].copy()
        grouped = df.groupby(rl(param["index_cols"]), as_index=False)
        df_new = grouped.apply(lambda x: calc_msd(
            x, param)).reset_index(drop=True)
        df_index = df.loc[:, param["index_cols"]].reset_index(drop=True)
        df = pd.concat([df_index, df_new], axis=1)
        return df


def calc_msd(df, param):
    """This function is used in :meth:`pandas.core.groupby.GroupBy.apply`
    of :class:`Each`.
    """
    msd = np.zeros(1)
    for i in range(1, len(df)):
        sd = 0
        for col in param["calc_cols"]:
            x = df[col].values
            sd += np.power((x[i:] - x[:-i]), 2)
        msd = np.append(msd, np.average(sd))
    interval = np.append(
        np.zeros(1), range(1, len(df))) * param["interval"]
    df = pd.DataFrame({"interval": interval, "msd": msd})
    return df.reset_index(drop=True)


class FitAnom(Table):
    """Fitting parameters fitted from MSD with 4Dt^a.

    If fitting is failed, this class returns initial values; D=value calculated
    from initial slope, alpha=0.5.

    Args:
        reqs[0] (Table): MSD Table. Required param; ``interval``,
            ``length_unit``. Required column; ``msd``.
        param["step"] (int): Step number for fitting from interval=0.
        param["group_depth"] (int): Data split depth for fitting.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Table containing the list of fitting parameters
    """

    def set_info(self, param):
        """Copy info from req[0] and add columns and params.
        """
        self.info.copy_req(0)
        self.info.set_group_depth(param["group_depth"])
        length_unit = self.info.get_param_value("length_unit")
        cols = self.info.get_param_value("index_cols")
        self.info.delete_column(keeps=cols)
        self.info.add_column(
            0, "diff_coeff", "float64", length_unit + "^2/s",
            "Diffusion coefficient")
        self.info.add_column(
            0, "alpha", "float64", "none", "Anomalous exponent")
        self.info.add_param(
            "step", param["step"], "num",
            "Step number for fitting from interval=0")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Fitting parameters fitted from MSD with 4Dt^a.

        If fitting is failed, this class returns initial values; D=value
        calculated from initial slope, alpha=0.5.

        Args:
            reqs[0] (pandas.DataFrame): MSD table containing ``interval`` and
                ``msd`` columns.
            param["step"] (int): Step number for fitting from interval=0.
            param["interval"] (float): Time interval in second.
            param["index_cols"] (list of str): Column names for index.

        Returns:
            pandas.DataFrame: List of fitting parameters
        """
        df = reqs[0].copy()
        if len(param["index_cols"]) > 0:
            grouped = df.groupby(rl(param["index_cols"]))
            df = grouped.apply(lambda x: fit_msd_anom(x, param))
            df = df.reset_index()
        else:
            s = fit_msd_anom(df, param)
            df = pd.DataFrame([s])
            df = df.reset_index(drop=True)
        return df


def fit_msd_anom(df, param):
    t = df["interval"].to_list()[:param["step"] + 1]
    msd = df["msd"].to_list()[:param["step"] + 1]
    t0 = t[1]
    msd0 = msd[1]
    try:
        popt, pcov = curve_fit(
            f=msd_anom_diff,
            xdata=t,
            ydata=msd,
            p0=(msd0 / (4 * t0), 0.5)
        )
    except (ValueError, RuntimeError, OptimizeWarning):
        popt = (msd0 / (4 * t0), 0.5)

    return pd.Series({"diff_coeff": popt[0], "alpha": popt[1]})


class ModelAnom(Table):
    """Model curve of MSD with 4Dt^a.

    Args:
        reqs[0] (FitAnom): Table containing fitting parameters of MSD with
            anomalous diffusion. Required columns; ``diff_coeff``, ``alpha``.
            Required params; ``length_unit``,
        param["x_lims"] (list of float): Minimum and maximum position of
            x-axis.
        param["step"] (float): Step size of x-axis for the model curve.
        param["group_depth"] (int): Data split depth.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Model curve Table
    """

    def set_info(self, param):
        """Copy info from req[0] and add columns and params.
        """
        self.info.copy_req(0)
        self.info.delete_column(keeps=self.info.get_column_name("index"))
        length_unit = self.info.get_param_value("length_unit")
        self.info.add_column(
            0, "interval", "float64", "s", "Time interval for MSD")
        self.info.add_column(
            0, "model", "float64", length_unit + "^2", "Model curve of MSD")
        self.info.add_param(
            "x_lims", param["x_lims"], "list of float64",
            "Minimum and maximum position of x-axis.")
        self.info.add_param(
            "step", param["step"], "float64",
            "Step size of x-axis for the model curve.")
        self.info.set_group_depth(param["group_depth"])
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Model curve of MSD with 4Dt^a.

        Args:
            reqs[0] (pandas.DataFrame): Fitting parameters of MSD with
                anomalous diffusion. Required columns; ``diff_coeff``,
                ``alpha``.
            param["x_lims"] (list of float): Minimum and maximum position of
                x-axis.
            param["step"] (float): Step size of x-axis for the model curve.
            param["index_cols"] (list of str): Column names of index.

        Returns:
            pandas.DataFrame: Model curve table
        """
        df = reqs[0].copy()
        if len(param["index_cols"]) > 0:
            dfs = []
            for _, row in df.groupby(rl(param["index_cols"])):
                df_index = pd.DataFrame(
                    [row.iloc[0, :len(param["index_cols"])]])\
                    .reset_index(drop=True)
                d = row["diff_coeff"].values[0]
                a = row["alpha"].values[0]
                x = np.arange(param["x_lims"][0],
                              param["x_lims"][1], param["step"])
                y = msd_anom_diff(x, d, a)
                df = pd.DataFrame({"interval": x, "model": y})
                df = pd.concat([df_index, df], axis=1).fillna(method="ffill")
                df[param["index_cols"]] = df[param["index_cols"]].astype(int)
                dfs.append(df)
            df = pd.concat(dfs)
        else:
            d = df["diff_coeff"].values[0]
            a = df.alpha[0]
            x = np.arange(param["x_lims"][0],
                          param["x_lims"][1], param["step"])
            y = msd_anom_diff(x, d, a)
            df = pd.DataFrame({"interval": x, "model": y})
        return df


class FitSimple(Table):
    """Diffusion coefficients from MSD fitted with a simple 4Dt.

    Args:
        reqs[0] (Table): MSD Table. Required columns; ``interval``, ``msd``.
            Required params; ``length_unit``,
        param["step"] (int): Step number for fitting from interval=0.
        param["group_depth"] (int): Data split depth for fitting.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Table containing the list of diffusion coefficient
    """

    def set_info(self, param):
        """Copy info from req[0] and add columns and params.
        """
        self.info.copy_req(0)
        self.info.set_group_depth(param["group_depth"])
        length_unit = self.info.get_param_value("length_unit")
        cols = self.info.get_param_value("index_cols")
        self.info.delete_column(keeps=cols)
        self.info.add_column(0, "diff_coeff", "float64",
                             length_unit + "^2/s",
                             "Diffusion coefficient")
        self.info.add_param("step", param["step"], "num",
                            "Step number for fitting from interval=0")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Diffusion coefficients from MSD fitted with a simple 4Dt.

        Args:
            reqs[0] (pandas.DataFrame): MSD table. Required columns;
                ``interval``, ``msd``.
            param["step"] (int): Step number for fitting from interval=0.
            param["index_cols"] (list of str): Column names of index.

        Returns:
            pandas.DataFrame: List of diffusion coefficient
        """
        df = reqs[0].copy()
        if len(param["index_cols"]) > 0:
            grouped = df.groupby(rl(param["index_cols"]))
            df = grouped.apply(lambda x: fit_msd_simple(x, param))
            df = df.reset_index()
        else:
            s = fit_msd_simple(df, param)
            df = pd.DataFrame([s])
            df = df.reset_index(drop=True)
        return df


def fit_msd_simple(df, param):
    t = df["interval"].to_list()[:param["step"] + 1]
    msd = df["msd"].to_list()[:param["step"] + 1]
    popt, pcov = curve_fit(
        f=msd_simple_diff,
        xdata=t,
        ydata=msd,
        p0=(msd[1] / (4 * t[1]))
    )
    return pd.Series({"diff_coeff": popt[0]})


def msd_simple_diff(t, d):
    """Model function for simple MSD fitting.

    Args:
        t (float): Time interval value.
        d (float): Diffusion coefficient.

    Returns:
        float: Mean square displacement
    """
    return 4 * d * t


def msd_anom_diff(t, d, a):
    """Model function for MSD fitting with anomalous diffusion.

    Args:
        t (float): Time interval value.
        d (float): Diffusion coefficient.
        a (float): Anomalous exponent. a should be > 0.

    Returns:
        float: Mean square displacement
    """
    return 4 * d * t ** a


class ModelSimple(Table):
    """Model curve of MSD with 4Dt.

    Args:
        reqs[0] (FitSimple): Table containing fitting parameters. Required
            column; ``diff_coeff``. Required params; ``length_unit``.
        param["x_lims"] (list of float): Minimum and maximum position of
            x-axis.
        param["step"] (float): The step size of x-axis of the model curve.
        param["group_depth"] (int): Data split depth to calculate model.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Model curve Table
    """

    def set_info(self, param):
        """Copy info from req[0] and add columns and params.
        """
        self.info.copy_req(0)
        self.info.delete_column(keeps=self.info.get_column_name("index"))
        length_unit = self.info.get_param_value("length_unit")
        self.info.add_column(
            0, "interval", "float64", "s", "Time interval for MSD")
        self.info.add_column(
            0, "model", "float64", length_unit + "^2", "Model curve of MSD")
        self.info.add_param(
            "x_lims", param["x_lims"], "list of float64",
            "Minimum and maximum position of x-axis")
        self.info.add_param(
            "step", param["step"], "float64",
            "Step size of x-axis of the model curve")
        self.info.set_group_depth(param["group_depth"])
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Model curve of MSD with 4Dt.

        Args:
            reqs[0] (pandas.DataFrame): Table containing fitting parameters.
                Required column; ``diff_coeff``.
            param["x_lims"] (list of float): Minimum and maximum position of
                x-axis.
            param["step"] (float): The step size of x-axis of the model curve.
            param["index_cols"] (list of str): Column names of index.

        Returns:
            pandas.DataFrame: Model curve Table

        """
        df = reqs[0].copy()
        if len(param["index_cols"]) > 0:
            dfs = []
            for _, row in df.groupby(rl(param["index_cols"])):
                df_index = pd.DataFrame(
                    [row.iloc[0, :len(param["index_cols"])]])\
                    .reset_index(drop=True)
                d = row["diff_coeff"].values[0]
                x = np.arange(param["x_lims"][0],
                              param["x_lims"][1], param["step"])
                y = msd_simple_diff(x, d)
                df = pd.DataFrame({"interval": x, "model": y})
                df = pd.concat([df_index, df], axis=1).fillna(method="ffill")
                df[param["index_cols"]] = df[param["index_cols"]].astype(int)
                dfs.append(df)
            df = pd.concat(dfs)
        else:
            d = df["diff_coeff"].values[0]
            x = np.arange(param["x_lims"][0],
                          param["x_lims"][1], param["step"])
            y = msd_simple_diff(x, d)
            df = pd.DataFrame({"interval": x, "model": y})
        return df


class DfromDeltaV(Table):
    """Diffusion coefficients from differential velocity with simple 4Dt.

    Args:
        reqs[0] (Table): Trajectory Table. Required columns;
            ``x_(length_unit)``, ``y_(length_unit)``. Required params;
            ``length_unit``.
        param["calc_cols"] (list of str): Column names to calculate diffusion
            coefficients.
        param["group_depth"] (int): Data split depth.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Diffusion coefficient of each trajectory
    """

    def set_info(self, param):
        """Copy info from req[0] and add columns and params.
        """
        self.info.copy_req()
        length_unit = self.info.get_param_value("length_unit")
        self.info.set_group_depth(param["group_depth"])
        self.info.delete_column(keeps=self.info.get_param_value("index_cols"))
        self.info.add_column(
            0, "diff_coeff", "float64", length_unit + "^2/s",
            "Diffusion coefficient")
        self.info.add_param(
            "calc_cols", ["x_" + length_unit, "y_" + length_unit],
            "list of str", "Diffusion coefficient calculation columns")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Diffusion coefficients from differential velocity with simple 4Dt.

        Args:
            reqs[0] (pandas.DataFrame): Trajectory Table. Required columns;
                ``x_(length_unit)``, ``y_(length_unit)``.
            param["calc_cols"] (list of str): Column names to calculate
                diffusion coefficients.
            param["index_cols"] (list of str): Column names of index.

        Returns:
            pandas.DataFrame: Diffusion coefficient of each trajectory
        """
        df = reqs[0].copy()
        grouped = df.groupby(rl(param["index_cols"]))
        df = grouped.apply(lambda x: calc_delta_v(x, param))
        return df.reset_index()


def calc_delta_v(df, param):
    dt = param["interval"]  # from copy_reqs
    v = np.empty(0)
    d = 0
    for col in param["calc_cols"]:
        x = df[col].values
        x -= np.mean(x)

        v_x = np.diff(x) / dt
        v = np.concatenate((v, v_x))

        msd_xt = np.dot(v_x, v_x) / len(v_x)
        d += msd_xt * dt / 4

    return pd.Series({"diff_coeff": d})


class FitConfSaxton(Table):
    """Fitting parameters fitted from MSD with Saxton confined model.

    This model is approximation of Appendix B B14 equation in Saxton, M.J.,
    1993. Biophys. J. 64, 1766-1780. Only n=1 is used from the
    summation in the equation.

    If fitting is failed, this class returns initial values; D=value calculated
    from initial slope, alpha=0.5.

    Args:
        reqs[0] (Table): MSD Table. Required param; ``length_unit``.
            Required columns; ``interval``, ``msd``.
        param["step"] (int): Step number for fitting from interval=0.
        param["group_depth"] (int): Data split depth.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Table containing the list of fitting parameters
    """

    def set_info(self, param):
        """Copy info from req[0] and add columns and params.
        """
        self.info.copy_req(0)
        self.info.set_group_depth(param["group_depth"])
        length_unit = self.info.get_param_value("length_unit")
        cols = self.info.get_param_value("index_cols")
        self.info.delete_column(keeps=cols)
        self.info.add_column(
            0, "diff_coeff", "float64", length_unit + "^2/s",
            "Diffusion coefficient")
        self.info.add_column(
            0, "r", "float64", length_unit, "Confinement radius")
        self.info.add_param(
            "step", param["step"], "num",
            "Step number for fitting from interval=0")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Fitting parameters fitted from MSD with Saxton confined model.

        If fitting is failed, this class returns initial values; D=value
        calculated from initial slope, r=final value of MSD.

        Args:
            reqs[0] (pandas.DataFrame): MSD table. Required columns;
                ``interval``, ``msd``.
            param["step"] (int): Step number for fitting from interval=0.
            param["interval"] (float): Time interval in second.
            param["index_cols"] (list of str): Column names for index.

        Returns:
            pandas.DataFrame: List of fitting parameters
        """
        df = reqs[0].copy()
        if len(param["index_cols"]) > 0:
            grouped = df.groupby(rl(param["index_cols"]))
            df = grouped.apply(lambda x: fit_msd_confs(x, param))
            df = df.reset_index()
        else:
            s = fit_msd_confs(df, param)
            df = pd.DataFrame([s])
            df = df.reset_index(drop=True)
        return df


def fit_msd_confs(df, param):
    t = df["interval"].to_list()[:param["step"] + 1]
    msd = df["msd"].to_list()[:param["step"] + 1]
    t0 = t[1]
    msd0 = msd[1]
    try:
        popt, pcov = curve_fit(
            f=msd_confs_diff,
            xdata=t,
            ydata=msd,
            p0=(msd0 / (4 * t0), np.sqrt(msd[-1]))
        )
    except (ValueError, RuntimeError, OptimizeWarning):
        popt = (msd0 / (4 * t0), np.sqrt(msd[-1]))

    return pd.Series({"diff_coeff": popt[0], "r": popt[1]})


def msd_confs_diff(t, d, r):
    """Model function for MSD fitting with confined diffusion.

    Args:
        t (float): Time interval value.
        d (float): Diffusion coefficient.
        r (float): Confinement radius.

    Returns:
        float: Mean square displacement
    """
    return (r ** 2) * (1 - 0.987428 * np.exp(-3.38996 * d * t / (r ** 2)))


class ModelConfSaxton(Table):
    """Model curve of MSD with Saxton confined model.

    Args:
        reqs[0] (FitConfSaxton): Table containing fitting parameters of MSD
            with confined diffusion. Required columns; ``diff_coeff``, ``r``.
            Required params; ``length_unit``.
        param["x_lims"] (list of float): Minimum and maximum position of
            x-axis.
        param["step"] (float): Step size of x-axis for the model curve.
        param["group_depth"] (int): Data split depth.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Model curve Table
    """

    def set_info(self, param):
        """Copy info from req[0] and add columns and params.
        """
        self.info.copy_req(0)
        self.info.delete_column(keeps=self.info.get_column_name("index"))
        length_unit = self.info.get_param_value("length_unit")
        self.info.add_column(
            0, "interval", "float64", "s", "Time interval for MSD")
        self.info.add_column(
            0, "model", "float64", length_unit + "^2", "Model curve of MSD")
        self.info.add_param(
            "x_lims", param["x_lims"], "list of float64",
            "Minimum and maximum position of x-axis.")
        self.info.add_param(
            "step", param["step"], "float64",
            "Step size of x-axis for the model curve.")
        self.info.set_group_depth(param["group_depth"])
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Model curve of MSD with Saxton confined model.

        Args:
            reqs[0] (pandas.DataFrame): Fitting parameters of MSD with
                confined diffusion. Required columns; ``diff_coeff``,
                ``r``.
            param["x_lims"] (list of float): Minimum and maximum position of
                x-axis.
            param["step"] (float): Step size of x-axis for the model curve.
            param["index_cols"] (list of str): Column names of index.

        Returns:
            pandas.DataFrame: Model curve table
        """
        df = reqs[0].copy()
        if len(param["index_cols"]) > 0:
            dfs = []
            for _, row in df.groupby(rl(param["index_cols"])):
                df_index = pd.DataFrame(
                    [row.iloc[0, :len(param["index_cols"])]])\
                    .reset_index(drop=True)
                d = row["diff_coeff"].values[0]
                r = row["r"].values[0]
                x = np.arange(param["x_lims"][0],
                              param["x_lims"][1], param["step"])
                y = msd_confs_diff(x, d, r)
                df = pd.DataFrame({"interval": x, "model": y})
                df = pd.concat([df_index, df], axis=1).fillna(method="ffill")
                df[param["index_cols"]] = df[param["index_cols"]].astype(int)
                dfs.append(df)
            df = pd.concat(dfs)
        else:
            d = df["diff_coeff"].values[0]
            r = df.r[0]
            x = np.arange(param["x_lims"][0],
                          param["x_lims"][1], param["step"])
            y = msd_confs_diff(x, d, r)
            df = pd.DataFrame({"interval": x, "model": y})
        return df
