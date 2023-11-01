import numpy as np
import matplotlib.pyplot as plt

from .figure import Figure
from .style import set_cmap


class Gray(Figure):
    """Create a pseudo color map from a grayscale image.

    .. caution::

        The image should be split into a single-frame image. In other
        words, the shape of reqs[0] in :meth:`process` should be (1,
        height, width).

    Args:
        reqs[0] (Image): Image to create image Figure. Required params;
            ``img_size``, ``pitch``.
        param["lut_limits"] (list of float, optional): Lower and upper limit of
            LUT. Defaults to [0, 1].
        param["cmap"] (str or list of int, optional): Color map name for
            `matplotlib.colormaps <https://matplotlib.org/stable/tutorials/colors/colormaps.html>`_.
            , or list of RGB values where each integer value is between 0 and
            255. e.g. [255, 0, 0 ] for red. Defaults to "gray".
        param["split_depth"] (int): The file split depth number.

    Returns:
        Figure: matplotlib Figure containing pseudo color image.
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add parameters.
        """
        self.info.copy_req(0)
        self.info.add_param(
            "lut_limits", param.get("lut_limits", [0, 1]),
            "list of float", "LUT lower and higher limit values")

        if "cmap" not in param:
            param["cmap"] = "gray"
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
            param["cmap"] (str or list of int, optional): Color map name for
                `matplotlib.colormaps <https://matplotlib.org/stable/tutorials/colors/colormaps.html>`_.
                , or list of RGB values where each integer value is between 0
                and 255. e.g. [255, 0, 0 ] for red. Defaults to "gray".
            param["pitch"] (float): The pixel size in length_unit/pix.
            param["img_size"] (list of int): The width and height of each image
                (pixels).

        Returns:
            matplotlib.figure.Figure: matplotlib Figure containing pseudo color
            image.
        """
        img = reqs[0].copy()
        if img.shape[0] != 1:
            raise ValueError(
                "Image should be split into a single frame image.")
        img = img[0, :, :]
        low, high = param["lut_limits"]
        width, height = param["img_size"][0] * \
            param["pitch"], param["img_size"][0] * param["pitch"]

        fig, ax = plt.subplots()
        ax.imshow(img, origin="lower", extent=[0, width, 0, height],
                  clim=(low, high), label="img")
        fig = set_cmap(fig, param["cmap"])
        return fig
