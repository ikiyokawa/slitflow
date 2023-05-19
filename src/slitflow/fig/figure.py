import io

import numpy as np
import cv2
import matplotlib
import matplotlib.pyplot as plt

from ..img.image import RGB
from ..data import Pickle
from .. import MATPLOTLIB_BACKEND

matplotlib.use(MATPLOTLIB_BACKEND)


class Figure(Pickle):
    """Figure Data saved as matplotlib pickle object.

    """
    EXT = '.fig'

    def __init__(self, info_path=None):
        super().__init__(info_path)

    def save_data(self, data, path):
        """
        :class:`matplotlib.axes.Axes` cannot be copied. All figures should be
        saved as a file after executing each process. You have to use run
        mode 2.
        """
        super().save_data(data, path)
        plt.close()


class ToTiff(RGB):
    """Convert matplotlib figure object to RGB tiff class.

    Args:
        reqs[0] (Figure): Figure class containing
            :class:`matplotlib.figure.Figure` objects.
        param["dpi"] (int, optional): Dot per inch of image. Defaults to 400.
        param["scalebar"] (list, optional): [length, left position, bottom
            position, line width, line color] of the scale bar. Positions
            should be the relative positions of figure size (0-1). Line color
            should be [R(0-255), G(0-255), B(0-255)]. This parameter requires
            "limit", "size" and "length_unit" to reqs[0].
        param["split_depth"] (int): File split depth number.

    Returns:
        slitflow.img.image.RGB: Image of figure
    """

    def set_info(self, param={}):
        """Copy information from reqs[0] and add parameters.
        """
        self.info.copy_req(0)
        if "dpi" not in param:
            param["dpi"] = 400
        self.info.add_param(
            "dpi", param["dpi"], "int", "Dot per inch of figure image")

        # use only x-axis for scale bar
        limit = self.info.get_param_value("limit")
        size = self.info.get_param_value("size")
        length_unit = self.info.get_param_value("length_unit")
        if limit and size and length_unit:
            pixel = size[0] / 2.54 * param["dpi"]
            if limit[0] is not None:
                pitch = (limit[1] - limit[0]) / pixel
                self.info.add_param(
                    "pitch", pitch, length_unit, "Pixel size of figure")
        if "scalebar" in param:
            self.info.add_param(
                "scalebar", param["scalebar"], "list",
                "[length, left, bottom , line_width, line_color] of the scale\
                 bar")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Convert matplotlib figure object to RGB tiff class.

        Args:
            reqs[0] (matplotlib.figure.Figure): Figure object.
            param["dpi"] (int, optional): Dot per inch of image. Defaults to
                400.
            param["scalebar"] (list, optional): [length, left position, bottom
                position, line width, line color] of the scale bar. Positions
                should be the relative positions of figure size (0-1).
                Line color should be [R(0-255), G(0-255), B(0-255)]. This
                parameter requires "limit", "size" and "length_unit" to
                reqs[0].
            param["limit"] (list of float, optional): [left, right, bottom,
                top] limits of figure axes. Required if ``scale`` in param.

        Returns:
            numpy.ndarray: Image of figure
        """
        fig = reqs[0]
        if "scalebar" in param:
            width = param["limit"][1] - param["limit"][0]
            height = param["limit"][3] - param["limit"][2]
            left = width * param["scalebar"][1] + param["limit"][0]
            bottom = height * param["scalebar"][2] + param["limit"][2]

            fig.axes[0].plot([left, left + param["scalebar"][0]],
                             [bottom, bottom], linewidth=param["scalebar"][3],
                             color=np.array(param["scalebar"][4]) / 255)

        stack = np.array(get_stack(fig, param["dpi"]))
        return stack


def get_stack(fig, dpi):
    """Convert matplotlib.figure.Figure to numpy.ndarray of RGB image.

    Args:
        fig (matplotlib.figure.Figure): Figure object.
        dpi (int): Dot per inch.

    Returns:
        numpy.ndarray: RGB image with the shape of (color, height, width)
    """
    stack = []
    fig.set_dpi(dpi)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi)
    buf.seek(0)
    fig_rgb = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    img = cv2.imdecode(fig_rgb, 1)
    fig_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    stack.append(np.flipud(fig_rgb[:, :, 0]))
    stack.append(np.flipud(fig_rgb[:, :, 1]))
    stack.append(np.flipud(fig_rgb[:, :, 2]))
    return stack


def inherit_split_depth(Data, reqs_no, group_depth):
    Data.info.set_group_depth(group_depth)
    split_depth = Data.reqs[reqs_no].info.split_depth_req
    keeps = Data.info.get_column_name("index")[:split_depth]
    Data.info.delete_column(keeps=keeps)
    Data.info.set_split_depth(split_depth)
