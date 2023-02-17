import numpy as np

import importlib  # for skimage

from ..img import image


class Gray(image.Image):
    """Create montage image from image stack.

    This class is brief wrapper of :func:`skimage.util.montage`.

    .. caution::

        The input image stack must be split so that all frames to be tiled into
        a montage image are included.

    Args:
        reqs[0] (Image): Image stack to create montage.
        param["grid_shape"] (tuple of int): See :func:`skimage.util.montage`.
        param["padding_width"] (int): See :func:`skimage.util.montage`.
        param["split_depth"] (int): File split depth number.

    Returns:
        Image: Montage Image
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        req_cols = self.reqs[0].info.get_column_name("index")
        req_cols = req_cols[:self.reqs[0].info.split_depth()]
        cols = self.reqs[0].info.get_column_name("col")
        self.info.copy_req(0, "column", req_cols + cols)
        self.info.copy_req(0, "param")
        self.info.add_param(
            "grid_shape", param["grid_shape"], "int",
            "grid_shape of skimage.util.montage")
        self.info.add_param(
            "padding_width", param["padding_width"], "int",
            "padding_width of skimage.util.montage")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Create montage image from image stack.

        Args:
            reqs[0] (numpy.ndarray): Numpy 3D array with the shape of
                (frame number, height, width).
            param["grid_shape"] (tuple of int): See
                :func:`skimage.util.montage`.
            param["padding_width"] (int): See
                :func:`skimage.util.montage`.

        Returns:
            numpy.ndarray: Montage image
        """
        util = importlib.import_module("skimage.util")
        img = reqs[0].copy()
        for i in range(img.shape[0]):
            img[i, :, :] = np.flipud(img[i, :, :])
        mtg = util.montage(img, grid_shape=param["grid_shape"],
                           padding_width=param["padding_width"], fill=0)
        mtg = np.flipud(mtg)
        mtg = mtg.reshape([1, mtg.shape[0], mtg.shape[1]])
        return mtg

    def post_run(self):
        """Update image size to montage image.
        """
        image.set_img_size(self)


class RGB(image.RGB):
    """Create montage image from RGB image stack.

    This class is brief wrapper of :func:`skimage.util.montage`.

    .. caution::

        The input image stack must be split so that all frames to be tiled into
        a montage image are included.

    Args:
        reqs[0] (Image): Image stack to create montage.
        param["grid_shape"] (tuple of int): See :func:`skimage.util.montage`.
        param["padding_width"] (int): See :func:`skimage.util.montage`.
        param["split_depth"] (int): File split depth number.

    Returns:
        Image: Montage Image
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        req_cols = self.reqs[0].info.get_column_name("index")
        req_cols = req_cols[:self.reqs[0].info.split_depth()]
        cols = self.reqs[0].info.get_column_name("col")
        cols = req_cols + ["color"] + cols
        self.info.copy_req(0, "column", cols)
        self.info.copy_req(0, "param")
        self.info.add_param(
            "grid_shape", param["grid_shape"], "int",
            "grid_shape of skimage.util.montage")
        self.info.add_param(
            "padding_width", param["padding_width"], "int",
            "padding_width of skimage.util.montage")
        self.info.set_split_depth(param["split_depth"])

    def set_index(self):
        """Use Image super class set_index.
        """
        image.Image.set_index(self)

    @staticmethod
    def process(reqs, param):
        """Create montage image from image stack.

        Args:
            reqs[0] (numpy.ndarray): Numpy 3D array with the shape of
                (frames including RGB color frames, height, width).
            param["grid_shape"] (tuple of int): See
                :func:`skimage.util.montage`.
            param["padding_width"] (int): See
                :func:`skimage.util.montage`.

        Returns:
            numpy.ndarray: Montage image
        """
        util = importlib.import_module("skimage.util")
        img = reqs[0].copy()
        rgbs = []
        for i in range(int(img.shape[0] / 3)):
            rgb = np.zeros((img.shape[1], img.shape[2], 3))
            rgb[:, :, 0] = np.flipud(img[3 * i, :, :])
            rgb[:, :, 1] = np.flipud(img[3 * i + 1, :, :])
            rgb[:, :, 2] = np.flipud(img[3 * i + 2, :, :])
            rgbs.append(rgb)
        mtg = util.montage(rgbs, grid_shape=param["grid_shape"],
                           padding_width=param["padding_width"],
                           fill=(0, 0, 0), channel_axis=3)
        rgb = np.zeros((3, mtg.shape[0], mtg.shape[1]))
        rgb[0, :, :] = np.flipud(mtg[:, :, 0])
        rgb[1, :, :] = np.flipud(mtg[:, :, 1])
        rgb[2, :, :] = np.flipud(mtg[:, :, 2])
        return rgb

    def post_run(self):
        """Update image size to montage image.
        """
        image.set_img_size(self)
