import numpy as np
import matplotlib.pyplot as plt

from .figure import Figure
from ..fun.misc import reduce_list as rl


class Gray(Figure):
    """Create pseudo color map from a gray scale Image object.

        .. caution::

            The image should be split into a single frame image. In other
            words, the shape of reqs[0] in :meth:`process` should be (1,
            height, width).

    Args:
        reqs[0] (Image): Image to create image Figure. Required params;
            ``img_size``, ``pitch``.
        param["lut_limits"] (list of float): Lower and upper limit of LUT.
        param["cmap"] (str, optional): Color map name for
                :func:`matplotlib.pyplot.imshow`. Defaults to "viridis".

    Returns:
        Figure: matplotlib Figure object
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        self.info.add_param(
            "lut_limits", param["lut_limits"], "list of float",
            "LUT lower and higher limit values")
        if "cmap" not in param:
            param["cmap"] = "viridis"
        self.info.add_param(
            "cmap", param["cmap"], "str", "Colormap type string")
        self.info.set_split_depth(param["split_depth"])
        index_cols = self.info.get_column_name("index")
        self.info.delete_column(keeps=index_cols[:self.info.split_depth()])

    @staticmethod
    def process(reqs, param):
        """Create pseudo color map from a gray scale image array.

        Args:
            reqs[0] (numpy.ndarray): Image to create image figure.
            param["lut_limits"] (list of float): Lower and upper limit of
                LUT.
            param["cmap"] (str): Color map name for
                :func:`matplotlib.pyplot.imshow`.

        Returns:
            matplotlib.figure.Figure:  matplotlib Figure containing
            pseudo color image
        """
        img = reqs[0].copy()[0, :, :]
        low = param["lut_limits"][0]
        high = param["lut_limits"][1]
        width = param["img_size"][0] * param["pitch"]
        height = param["img_size"][0] * param["pitch"]

        fig, ax = plt.subplots()
        ax.imshow(img, origin="lower", extent=[0, width, 0, height],
                  clim=(low, high), cmap=param["cmap"], label="img")
        return fig
