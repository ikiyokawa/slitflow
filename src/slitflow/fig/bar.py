import matplotlib.pyplot as plt

from .figure import Figure, inherit_split_depth
from ..fun.misc import reduce_list as rl


class Simple(Figure):
    """Bar graph with or without error bar.

    Args:
        reqs[0] (Table): Table containing X and Y axes to create figure.
        param["calc_cols"] (list of str): Column names for X and Y axes.
        param["bar_widths"] (float or list of float, optional): Width of
            each bar. Defaults to 0.8.
        param["err_col"] (str, optional): Column name for error bar.
        param["cap_size"] (float, optional): Cap size of error bar.
        param["group_depth"] (int): Data split depth number.

    Returns:
        Figure: Bar Figure object
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        inherit_split_depth(self, 0, param["group_depth"])

        self.info.add_param(
            "calc_cols", param["calc_cols"], "str", "X and Y columns")
        if "bar_widths" not in param:
            param["bar_widths"] = 0.8
        self.info.add_param(
            "bar_widths", param["bar_widths"], "float or list",
            "Width of each bar")
        if "err_col" in param:
            self.info.add_param(
                "err_col", param["err_col"], "str", "Error bar column")
            if "cap_size" not in param:
                param["cap_size"] = 2
            self.info.add_param(
                "cap_size", param["cap_size"], "float", "Error bar cap size")

    @staticmethod
    def process(reqs, param):
        """Bar graph with or without error bar.

        Args:
            reqs[0] (pandas.DataFrame): Table containing X and Y axes to create
                figure.
            param["calc_cols"] (list of str): Column names for X and Y axes.
            param["bar_widths"] (float or list of float): Width of each bar.
            param["err_col"] (str, optional): Column name for error bar.
            param["cap_size"] (float): Cap size of error bar.
            param["index_cols"] (list of str): Column names of index.
                These column names are used for
                :meth:`pandas.DataFrame.groupby`.

        Returns:
            matplotlib.figure.Figure:  matplotlib Figure containing bar plot
        """
        df = reqs[0].copy()
        fig, ax = plt.subplots()
        if len(param["index_cols"]) == 0:
            x = df[param["calc_cols"][0]].values
            y = df[param["calc_cols"][1]].values
            if "err_col" in param:
                sd = df[param["err_col"]].values
                ax.bar(x, y, yerr=sd, ecolor="black",
                       capsize=param["cap_size"], label="bar",
                       width=param["bar_widths"])
            else:
                ax.bar(x, y, label="bar",
                       width=param["bar_widths"])
        else:
            for i, (_, row) in enumerate(df.groupby(rl(param["index_cols"]))):
                x = row[param["calc_cols"][0]].values
                y = row[param["calc_cols"][1]].values
                if "err_col" in param:
                    sd = row[param["err_col"]].values
                    ax.bar(x, y, yerr=sd, capsize=param["cap_size"],
                           label="bar" + str(i + 1),
                           width=param["bar_widths"])
                else:
                    ax.bar(x, y, label="bar" + str(i + 1),
                           width=param["bar_widths"])
        return fig


class WithModel(Figure):
    """Bar graph with or without error bar and with model curves.

    Args:
        reqs[0] (Table): Table containing X and Y axes of raw data.
        reqs[1] (Table): Table containing X and Y axes of model curve.
        param["calc_cols"] (list of str): Column names for X and Y axes.
        param["err_col"] (str, optional): Column name for error bar.
        param["model_cols"] (list of str): Column names for X and Y axes of
            model curves.
        param["cap_size"] (float, optional): Cap size of error bar.
            Required if "err_col" in param. Defaults to 2.
        param["group_depth"] (int): Data split depth number.
        param["group_depth_model"] (int): Depth number to split model data.

    Returns:
        Figure: Bar Figure object with error and model
    """

    def set_info(self, param={}):
        self.info.copy_req(0)
        inherit_split_depth(self, 0, param["group_depth"])
        self.info.add_param(
            "calc_cols", param["calc_cols"], "str", "Columns to calculate")
        if "err_col" in param:
            self.info.add_param(
                "err_col", param["err_col"], "str", "Error bar column")
            if "cap_size" not in param:
                param["cap_size"] = 2
            self.info.add_param(
                "cap_size", param["cap_size"], "float", "Error bar cap size")
        self.info.add_param(
            "model_cols", param["model_cols"], "str", "Model columns")
        index_cols_model = self.reqs[1].info.get_column_name(
            "index")[:param["group_depth_model"]]
        self.info.add_param(
            "index_cols_model", index_cols_model, "list of str",
            "Index column names of model curve")

    @staticmethod
    def process(reqs, param):
        """Bar graph with or without error bar and with model curves.

        Args:
            reqs[0] (pandas.DataFrame): Table containing X and Y axes to create
                figure.
            param["calc_cols"] (list of str): Column names for X and Y axes.
            param["err_col"] (str, optional): Column name for error bar.
            param["model_cols"] (list of str): Column names for X and Y axes of
                model curves.
            param["index_cols"] (list of str): Column names of index.
                This column is used for :meth:`pandas.DataFrame.groupby`.
            param["cap_size"] (float, optional): Cap size of error bar.
                Required if "err_col" in param.
            param["index_cols_model"] (list of str): Column names of
                index. This column is used for :meth:`pandas.DataFrame.groupby`
                of model.

        Returns:
            matplotlib.figure.Figure: matplotlib Figure containing bar plot
            with model
        """
        df = reqs[0].copy()
        df_model = reqs[1].copy()
        fig, ax = plt.subplots()
        zorder = 1
        if len(param["index_cols"]) > 0:
            for i, (_, row) in enumerate(df.groupby(rl(param["index_cols"]))):
                x = row[param["calc_cols"][0]].values
                y = row[param["calc_cols"][1]].values
                if len(x) == 1:
                    bar_width = 0.8
                else:
                    bar_width = x[1] - x[0]
                if "err_col" in param:
                    sd = row[param["err_col"]].values
                    ax.bar(x, y, yerr=sd,
                           capsize=param["cap_size"], zorder=zorder,
                           width=bar_width, align="center",
                           label="bar" + str(i + 1))
                else:
                    ax.bar(x, y, label="plot" + str(i + 1), zorder=zorder,
                           width=bar_width, align="center")
                zorder += 1
            for i, (_, row) in enumerate(
                    df_model.groupby(rl(param["index_cols_model"]))):
                x = row[param["model_cols"][0]].values
                y = row[param["model_cols"][1]].values
                ax.plot(x, y, zorder=zorder, label="model" + str(i + 1))
                zorder += 1
        else:
            x = df[param["calc_cols"][0]].values
            y = df[param["calc_cols"][1]].values
            if len(x) == 1:
                bar_width = 0.8
            else:
                bar_width = x[1] - x[0]
            if "err_col" in param:
                sd = df[param["err_col"]].values
                ax.bar(x, y, yerr=sd,
                       capsize=param["cap_size"], zorder=zorder,
                       width=bar_width, align="center",
                       label="bar")
            else:
                ax.bar(x, y, zorder=zorder, label="plot")
            zorder += 1
            x = df_model[param["model_cols"][0]].values
            y = df_model[param["model_cols"][1]].values
            ax.plot(x, y, zorder=zorder, label="model")
        return fig
