import matplotlib.pyplot as plt

from .figure import Figure, inherit_split_depth
from ..fun.misc import reduce_list as rl


class Simple(Figure):
    """Line graph with or without error bar.

    Args:
        reqs[0] (Table): Table containing X and Y axes to create figure.
        param["calc_cols"] (list of str): Column names for X and Y axes.
        param["err_col"] (str, optional): Column name for error bar.
        param["cap_size"] (float, optional): Cap size of error bar.
            Required if "err_col" in param. Defaults to 2.
        param["group_depth"] (int): Data split depth number. This depth splits
            data for plotting. The split data is plotted as different lines.
            For example, if you want to plot each trajectory from a table
            containing column names "img_no" and "trj_no", you have to set
            group_depth=2. If you set group_depth=1, all trajectories are
            misconnected to each other.

    Returns:
        Figure: Line Figure object
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        inherit_split_depth(self, 0, param["group_depth"])
        self.info.add_param(
            "calc_cols", param["calc_cols"], "str", "X and Y columns")
        if "err_col" in param:
            self.info.add_param(
                "err_col", param["err_col"], "str", "Error bar column")
            if "cap_size" not in param:
                param["cap_size"] = 2
            self.info.add_param(
                "cap_size", param["cap_size"], "float", "Error bar cap size")

    @staticmethod
    def process(reqs, param):
        """Line graph with or without error bar.

        Args:
            reqs[0] (pandas.DataFrame): Table containing X and Y axes to create
                figure.
            param["calc_cols"] (list of str): Column names for X and Y axes.
            param["err_col"] (str, optional): Column name for error bar.
            param["cap_size"] (float, optional): Cap size of error bar.
                Required if "err_col" in param.
            param["index_cols"] (list of str): Column names of index.
                These column names are used for
                :meth:`pandas.DataFrame.groupby`.

        Returns:
            matplotlib.figure.Figure:  matplotlib Figure containing line plot
        """
        df = reqs[0].copy()
        fig, ax = plt.subplots()
        if len(param["index_cols"]) == 0:
            x = df[param["calc_cols"][0]].values
            y = df[param["calc_cols"][1]].values
            if "err_col" in param:
                sd = df[param["err_col"]].values
                ax.errorbar(x, y, yerr=sd, capsize=param["cap_size"],
                            label="errorbar")
            else:
                ax.plot(x, y, label="plot")
        else:
            for i, (_, row) in enumerate(df.groupby(rl(param["index_cols"]))):
                x = row[param["calc_cols"][0]].values
                y = row[param["calc_cols"][1]].values
                if "err_col" in param:
                    sd = row[param["err_col"]].values
                    ax.errorbar(x, y, yerr=sd, capsize=param["cap_size"],
                                label="errorbar" + str(i + 1))
                else:
                    ax.plot(x, y, label="plot" + str(i + 1))
        return fig


class WithModel(Figure):
    """Line with model curves.

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
        Figure: Line Figure object with error and model
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
        """Line with model curves.

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
            matplotlib.figure.Figure: matplotlib Figure containing line plot
            with model
        """
        df = reqs[0].copy()
        df_model = reqs[1].copy()
        fig, ax = plt.subplots()
        zorder = 1
        if len(param["index_cols"]) > 0:
            for i, (_, row) in enumerate(
                    df_model.groupby(rl(param["index_cols_model"]))):
                x = row[param["model_cols"][0]].values
                y = row[param["model_cols"][1]].values
                ax.plot(x, y, zorder=zorder, label="model" + str(i + 1))
                zorder += 1
            for i, (_, row) in enumerate(df.groupby(rl(param["index_cols"]))):
                x = row[param["calc_cols"][0]].values
                y = row[param["calc_cols"][1]].values
                if "err_col" in param:
                    sd = row[param["err_col"]].values
                    ax.errorbar(x, y, yerr=sd, linestyle='None', marker='o',
                                capsize=param["cap_size"], zorder=zorder,
                                label="errorbar" + str(i + 1))
                else:
                    ax.plot(x, y, label="plot" + str(i + 1))
                zorder += 1
        else:
            x = df_model[param["model_cols"][0]].values
            y = df_model[param["model_cols"][1]].values
            ax.plot(x, y, zorder=zorder, label="model")
            zorder += 1
            x = df[param["calc_cols"][0]].values
            y = df[param["calc_cols"][1]].values
            if "err_col" in param:
                sd = df[param["err_col"]].values
                ax.errorbar(x, y, yerr=sd, linestyle='None', marker='o',
                            capsize=param["cap_size"], zorder=zorder,
                            label="eroorbar")
            else:
                ax.plot(x, y, zorder=zorder, label="plot")

        return fig
