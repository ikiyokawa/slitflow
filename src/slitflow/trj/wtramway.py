"""
.. caution::

    This module consists of brief wrapper classes of
    `TRamWAy <https://github.com/DecBayComp/TRamWAy>`_ package.

    Wrapper classes do not cover all functionality of TRamWAy functions.
    Please create your custom class to use TRamWAy functions that are not
    provided in this module.

    Do not ask the TRamWAy developers any questions about the wrapper part
    that is not directly related to the TRamWAy package.

Please cite the following publication of the original package if you use
this module.

.. code-block:: text

    Laurent F, Verdier H, Duval M, Serov A, Vestergaard CL, Masson JB.
    TRamWAy: mapping physical properties of individual biomolecule random
    motion in large-scale single-particle tracking experiments.
    Bioinformatics. 2022 May 26;38(11):3149-3150.

"""

import importlib  # for tramway  # visual studio 2008 c++ runtime required
import matplotlib.pyplot as plt

from ..data import Pickle
from ..fig.figure import Figure


class Tessellation(Pickle):
    """Brief wrapper of tessellation of the TRamWay helper module.

    See also the documentation of `tramway.helper.tessellation.tessellate
    <https://tramway.readthedocs.io/en/latest/tramway.helper.html>`_.

    .. caution::

        Trajectories should be split into groups that you want to calculate as
        one map. e.g. single cell nucleus and single cell surface.

    Args:
        reqs[0] (Table): X,Y-coordinate of trajectory. Required param;
            ``length_unit``, ``interval``. Required columns; ``trj_no``,
            ``frm_no``, ``x_(length_unit)``, ``y_(length_unit)``.
        param["method"] (str): Tessellation method. See also the TRamWay
            documentation. This should be "grid", "hexagon", "kdtree",
            "kmeans", "gwr".
        param["param"] (dict, optional): Additional parameters to the 
            tessellation function.
        param["split_depth"] (int): File split depth number.

    Returns:
        Pickle: Partition object containing 
        :class:`tramway.tessellation.base.Partition`
    """

    def set_info(self, param):
        """Copy info from reqs[0] and set parameters.
        """
        self.info.copy_req(0)
        index_cols = self.info.get_column_name("index")
        self.info.delete_column(keeps=index_cols[:param["split_depth"]])
        length_unit = self.info.get_param_value("length_unit")
        self.info.add_param(
            "calc_cols", ["x_" + length_unit, "y_" + length_unit],
            "list of str", "Calculation Columns")
        self.info.add_param(
            "method", param["method"], "str", "Tessellation method name")
        if "param" in param:
            self.info.add_param(
                "param", param["param"], "dict",
                "Additional parameters to pass to the tessellation function")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Brief wrapper of tessellation of the TRamWay helper module.

        Args:
            reqs[0] (Table): X,Y-coordinate of trajectory. Required param;
                ``length_unit`` and ``interval``. Required columns; ``trj_no``,
                ``frm_no``, ``x_(length_unit)`` and ``y_(length_unit)``.
            param["method"] (str): Tessellation method. See also the TRamWay
                documentation. This should be "grid", "hexagon", "kdtree",
                "kmeans" or "gwr".
            param["param"] (dict, optional): Additional parameters to the
                tessellation function.
            param["calc_cols"] (list of str): Column names of X,Y-coordinate.
            param["interval"] (float): Time interval in second.

        Returns:
            tramway.tessellation.base.Partition: Partition object of TRamWay
        """
        helper = importlib.import_module("tramway.helper")
        df = reqs[0].copy()

        df_grp = df[["trj_no", param["calc_cols"]
                     [0], param["calc_cols"][1], "frm_no"]]
        df_grp = df_grp.rename(
            columns={"trj_no": "n", param["calc_cols"][0]: "x",
                     param["calc_cols"][1]: "y", "frm_no": "t"})
        df["t"] = df_grp["t"] * param["interval"]
        if "param" in param:
            P = helper.tessellate(df_grp, param["method"], **param["param"])
        else:
            P = helper.tessellate(df_grp, param["method"])
        return P


class Inference(Pickle):
    """Brief wrapper of inference of the TRamWay helper module.

    See also the documentation of `tramway.helper.inference.infer
    <https://tramway.readthedocs.io/en/latest/tramway.helper.html>`_.

    .. caution::

        This class uses multi processing. Do not use run mode 1 and 3.

    Args:
        reqs[0] (Tessellation): Wrapped class object of the TRamWay
            tessellation.
        param["mode"] (str): Inference mode string. This should be ``d``,
            ``dd``, ``df`` or ``dv``.
        param["param"] (dict, optional): Additional parameters to the 
            inference function.

    Returns:
        Pickle: Map object containing tramway.inference.base.Maps of TRamWay
    """

    def set_info(self, param):
        """Copy info from reqs[0] and set parameters.
        """
        self.info.copy_req(0)
        split_depth = self.reqs[0].info.split_depth()
        self.info.add_param(
            "mode", param["mode"], "str", "Tessellation method name")
        if "param" in param:
            self.info.add_param(
                "param", param["param"], "dict",
                "Additional parameters to pass to the inference function")
        self.info.set_split_depth(split_depth)

    @ staticmethod
    def process(reqs, param):
        """Brief wrapper of inference of the TRamWay helper module.

        Args:
            reqs[0] (tramway.tessellation.base.Partition): TRamWay
                tessellation object.
            param["mode"] (str): Inference mode string. This should be ``d``,
                ``dd``, ``df`` or ``dv``.
            param["param"] (dict, optional): Additional parameters to the 
                inference function.

        Returns:
            tramway.inference.base.Maps: Map object of TRamWay
        """
        inference = importlib.import_module("tramway.helper.inference")
        P = reqs[0]
        if "param" in param:
            M = inference.infer(P, param["mode"], **param["param"])
        else:
            M = inference.infer(P, param["mode"])
        return M


class MapPlot(Figure):
    """Brief wrapper of map_plot of the TRamWay helper module.

    See also the documentation of `tramway.helper.inference.map_plot
    <https://tramway.readthedocs.io/en/latest/tramway.helper.html>`_.

    Args:
        reqs[0] (Tessellation): Wrapped class object of the TRamWay
            tessellation.
        reqs[1] (Inference): Wrapped class object of the TRamWay inference.
        param["feature"] (str): Feature name for plotting. This should be
            ``diffusivity`` , ``force``, ``potential``, ``drift``
            depended on ``mode`` parameter of inference.
        param["param"] (dict, optional): Additional parameters to the 
            map_plot function.

    Returns:
        Figure: Feature Figure object
    """

    def set_info(self, param):
        """Copy info from reqs[0] and set parameters.
        """
        self.info.copy_req(0)
        split_depth = self.reqs[0].info.split_depth()
        self.info.add_param(
            "feature", param["feature"], "str", "Feature name for plotting")
        if "param" in param:
            self.info.add_param(
                "param", param["param"], "dict",
                "Additional parameters to pass to the map_plot function")
        self.info.set_split_depth(split_depth)

    @ staticmethod
    def process(reqs, param):
        """Brief wrapper of map_plot of the TRamWay helper module.

        See also the documentation of `tramway.helper.inference.map_plot
        <https://tramway.readthedocs.io/en/latest/tramway.helper.html>`_.

        Args:
            reqs[0] (tramway.tessellation.base.Partition): TRamWay
                tessellation object.
            reqs[1] (tramway.inference.base.Maps): Wrapped class object of the
                TRamWay inference.
            param["feature"] (str): Feature name for plotting. This should be
                ``diffusivity`` , ``force``, ``potential`` or ``drift``.
            param["param"] (dict, optional): Additional parameters to the 
                map_plot function.

        Returns:
            matplotlib.figure.Figure: matplotlib Figure object
        """
        helper = importlib.import_module("tramway.helper")
        P = reqs[0]
        T = reqs[1]

        plt.clf()
        if "param" in param:
            M = helper.map_plot(
                T, P, feature=param["feature"], **param["param"])
        else:
            M = helper.map_plot(T, P, feature=param["feature"])
        fig = M[0]
        unit = fig.axes[1].yaxis.get_label_text()
        label = param["feature"].capitalize() + " (" + unit + ")"
        fig.axes[0].yaxis.set_label_text(label)
        fig.axes[1].remove()
        return fig

    def post_run(self):
        """Save the color bar label of the figure as parameter.
        """
        label = self.data[0].axes[0].yaxis.get_label_text()
        self.info.add_param("label", label, "str", "Color bar label string")
