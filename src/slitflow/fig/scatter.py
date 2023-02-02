import pandas as pd
import matplotlib.pyplot as plt

from .figure import Figure
from . import style
from ..fun.misc import reduce_list as rl


class Simple(Figure):
    """Scatter plot of columns from a table.

    Args:
        reqs[0] (Table): Table containing X and Y axes to create figure.
        param["calc_cols"] (list of str): Column names for X and Y axes.
        param["marker_styles"] (str or list of str): Marker style of each
            group. Defaults to "o".
        param["group_depth"] (int): Data split depth number.
        param["split_depth"] (int): File split depth number.

    Returns:
        Figure: matplotlib figure objects.
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        self.info.delete_column(keeps=self.info.get_column_name("index"))
        self.info.add_param(
            "calc_cols", param["calc_cols"], "str", "X and Y columns")
        self.info.add_param(
            "marker_styles", param["marker_styles"], "list of str",
            "Marker style of each group")
        self.info.set_group_depth(param["group_depth"])
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Scatter plot of columns from a table.

        Args:
            reqs[0] (pandas.DataFrame): Table containing X and Y axes to create
                figure.
            param["calc_cols"] (list of str): Column names for X and Y axes.
            param["marker_styles"] (list of str): Marker style of each group.
                Defaults to "o".
            param["index_cols"] (list of str, optional): Column names of index.
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
            ax.scatter(x, y, label="scatter", marker=param["marker_styles"])
        else:
            for i, (_, row) in enumerate(df.groupby(rl(param["index_cols"]))):
                x = row[param["calc_cols"][0]].values
                y = row[param["calc_cols"][1]].values
                if type(param["marker_styles"]) == str:
                    ax.scatter(x, y, marker=param["marker_styles"],
                               label="scatter" + str(i + 1))
                else:
                    ax.scatter(x, y, marker=param["marker_styles"][i],
                               label="scatter" + str(i + 1))
        return fig
