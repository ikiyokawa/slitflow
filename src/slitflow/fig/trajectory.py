import numpy as np
import matplotlib.pyplot as plt

from .style import Basic
from .figure import Figure, inherit_split_depth
from ..fun.misc import reduce_list as rl


class All(Figure):
    """Show all trajectories of each image.

    Args:
        reqs[0] (Table): X,Y-coordinate of trajectories. Required param;
            ``length_unit``.
        param["trj_depth"] (int): Column depth of trajectory number.
        param["centered"] (bool, optional): If True, the centroid position from
            all trajectory positions is set as (0, 0).

    Returns:
        Figure: Trajectory Figure object
    """

    def set_info(self, param={}):
        """Copy and modify info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        inherit_split_depth(self, 0, param["trj_depth"])
        length_unit = self.info.get_param_value("length_unit")
        self.info.add_param(
            "calc_cols", ["x_" + length_unit, "y_" + length_unit],
            "list of str", "X,Y-coordinate columns")

        if ("centered", True) in param.items():
            self.info.add_param(
                "centered", param["centered"], "bool",
                "Whether to set the centroid of positions to zero")

    @staticmethod
    def process(reqs, param):
        """Show all trajectories of each image.

        Args:
            reqs[0] (pandas.DataFrame): X,Y-coordinate of trajectories.
            param["calc_cols"] (list of str): Column names for X and Y axes.
            param["index_cols"] (list of str): Column names of index.
                This column is used for :meth:`pandas.DataFrame.groupby`.
            param["centered"] (bool, optional): If True, the centroid position
                from all trajectory positions is set as (0, 0).

        Returns:
            matplotlib.figure.Figure: matplotlib Figure containing trajectory
            plot
        """
        df = reqs[0].copy()

        if ("centered", True) in param.items():
            xc = (np.max(df[param["calc_cols"][0]].values)
                  + np.min(df[param["calc_cols"][0]].values)) / 2
            yc = (np.max(df[param["calc_cols"][1]].values)
                  + np.min(df[param["calc_cols"][1]].values)) / 2
        else:
            xc = 0
            yc = 0

        fig, ax = plt.subplots()
        for i, (_, df_trj) in enumerate(df.groupby(rl(param["index_cols"]))):
            ax.plot(df_trj[param["calc_cols"][0]].values - xc,
                    df_trj[param["calc_cols"][1]].values - yc,
                    label="line" + str(i + 1))
        return fig


class StyleAll(Basic):
    """Simplified styling class for trajectory Figure.

    Args:
        reqs[0] (Figure): Trajectory Figure.
        param["half_width"] (float, optional): Half width of rendering axes in
            ``length_unit``. Used if trajectory is centered.

    Returns:
        Figure: Styled Figure object
    """

    def set_info(self, param={}):
        """Set default param then run super().set_info.
        """
        if "size" not in param:
            param["size"] = [4, 4]
        if "margin" not in param:
            param["margin"] = [0, 0, 0, 0]
        if "line_widths" not in param:
            param["line_widths"] = [0.2]
        if "line_colors" not in param:
            param["line_colors"] = [[0, 0, 0]]
        if "is_box" not in param:
            param["is_box"] = False

        req_param = self.reqs[0].info.get_param_dict()
        if ("centered", True) in req_param.items():
            if "half_width" in param:
                hw = param["half_width"]
                param["limit"] = [-hw, hw, -hw, hw]
            else:
                param["limit"] = [-10, 10, -10, 10]
        elif ("img_size" in req_param) & ("pitch" in req_param):
            # set limit to image edges
            param["limit"] = [0, req_param["img_size"][0] * req_param["pitch"],
                              0, req_param["img_size"][1] * req_param["pitch"]]
        if "limit" in param:  # to remove tick line
            param["tick"] = [
                [param["limit"][0] - 1, param["limit"][1] + 1],
                [param["limit"][2] - 1, param["limit"][3] + 1]]
        super().set_info(param)
