import pandas as pd

from ..tbl.table import Table
from ..fun.misc import reduce_list as rl


class Subtrajectory(Table):
    """Break down a trajectory into multiple subtrajectories.

    Reference:
        Ito, Y., Sakata-Sogawa, K. & Tokunaga, M. Multi-color single-molecule
        tracking and subtrajectory analysis for quantification of
        spatiotemporal dynamics and kinetics upon T cell activation.
        Sci Rep 7, 6994 (2017). https://doi.org/10.1038/s41598-017-06960-z


    Args:
        reqs[0] (Trajectory): Trajectory data.
        param["step"] (int): Step number of the subtrajectory. An N-step
            subtrajectory consists of N + 1 localizations.
        param["group_depth"] (int): Groupby depth.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Subtrajectory Table.
    """

    def set_info(self, param={}):
        """Insert a subtrj_no column and add parameters."""
        self.info.copy_req(0)
        cols = self.info.get_column_name("index")[:param["group_depth"]]
        self.info.add_param("split_cols", cols,
                            "list of str", "Index columns for groupby")
        self.info.reset_depth("frm_no", param["group_depth"] + 2)
        self.info.add_column(param["group_depth"] + 1, "subtrj_no", "int32",
                             "no", "Subtrajectory number")
        self.info.sort_column()
        index_cols = self.info.get_column_name("index")
        self.info.add_param("index_cols", index_cols,
                            "list of str", "Index columns for sorting")
        self.info.add_param("step", param["step"], "int32",
                            "Step number for subtrajectory")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Break down a trajectory into multiple subtrajectories.

        Args:
            reqs[0] (Trajectory): Trajectory data.
            param["step"] (int): Step number of the subtrajectory.
            param["split_cols"] (list of str): Index columns for groupby.
            param["index_cols"] (list of str): Index columns for sorting.

        Returns:
            Table: Subtrajectory Table.
        """
        df = reqs[0].copy()
        grouped = df.groupby(rl(param["split_cols"]))
        df_new = grouped.apply(lambda x: calc_subtrj(
            x, param)).reset_index(drop=True)
        cols = list(df_new.columns)
        value_cols = [x for x in cols if x not in param["index_cols"]]
        all_cols = param["index_cols"]
        all_cols.extend(value_cols)
        return df_new.reindex(columns=all_cols)


def calc_subtrj(df, param):
    """Break down a trajectory into multiple subtrajectories using rolling.

    The code calculates rolling windows of a specified size on a given
    DataFrame and adds a new column indicating the subtrajectory number for
    each window.

    Args:
        df (pandas.DataFrame): Trajectory data.
        param["step"] (int): Step number of subtrajectory.

    Returns:
        pandas.DataFrame: Subtrajectory DataFrame.
    """
    dfs = list(df.rolling(param["step"] + 1))[param["step"]:]
    dfs_new = [df.assign(subtrj_no=i + 1) for i, df in enumerate(dfs)]
    return pd.concat(dfs_new)
