from ..tbl.table import Table
from ..fun.misc import reduce_list as rl


class StepAtLeast(Table):
    """Select trajectories by the step number.

    Args:
        reqs[0] (Table): Trajectory data.
        param["step"] (int): Step number for selection. If you set step=2,
            trajectories containing at least three points (frames) are
            selected.
        param["group_depth"] (int): Depth number of trajectory number column.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Selected trajectory Table
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        self.info.add_param(
            "step", param["step"], "int32",
            "Step number for trajectory selection")
        self.info.set_group_depth(param["group_depth"])
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Select trajectories by the step number.

        Args:
            reqs[0] (pandas.DataFrame): Trajectory data.
            param["index_cols"] (list of str): Index column names for
                :meth:`pandas.DataFrame.groupby`. List should include the
                trajectory number column.

        Returns:
            pandas.DataFrame: Selected trajectory table
        """
        df = reqs[0].copy()
        grouped = df.groupby(rl(param["index_cols"]))
        df = grouped.filter(lambda x: len(x) > param["step"])
        return df.reset_index(drop=True)


class StepRange(Table):
    """Select trajectories by the step number range.

    Args:
        reqs[0] (Table): Trajectory data.
        param["step_range"] (list of int): Minimum and maximum numbers of
            trajectory step.
        param["group_depth"] (int): Data split depth number.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Selected trajectory Table
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        self.info.add_param(
            "step_range", param["step_range"], "list of int",
            "Minimum and maximum numbers of the trajectory step")
        self.info.set_group_depth(param["group_depth"])
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Select trajectories by the step number range.

        Args:
            reqs[0] (pandas.DataFrame): Trajectory data.
            param["step_range"] (list of int): Minimum and maximum numbers
                of trajectory step.
            param["index_cols"] (list of str): Index column names for
                :meth:`pandas.DataFrame.groupby`. List should include the
                trajectory number column.

        Returns:
            pandas.DataFrame: Selected trajectory table
        """
        df = reqs[0].copy()
        grouped = df.groupby(rl(param["index_cols"]))
        df = grouped.filter(lambda x: len(x) > param["step_range"][0])
        grouped = df.groupby(rl(param["index_cols"]))
        df = grouped.filter(lambda x: len(x) <= param["step_range"][1] + 1)
        return df.reset_index(drop=True)
