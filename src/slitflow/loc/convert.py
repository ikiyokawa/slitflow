import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, find

from ..tbl.table import Table, merge_different_index
from ..img.filter import DifferenceOfGaussian, LocalMax


class LocalMax2Xy(Table):
    """Convert nonzero local max pixels to X,Y-coordinate.

    .. caution::

        The input image should be split into a single frame image. In other
        words, the shape of reqs[0] in :meth:`process()` should be (1, height,
        width).

    Args:
        reqs[0] (LocalMax): Local max images to pick up coordinates. Required
            params; ``length_unit``, ``pitch``.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: X,Y-coordinate of local max pixels

    """

    def set_info(self, param):
        """Copy info from reqs[0] and add columns.
        """
        self.info.copy_req(0)
        length_unit = self.info.get_param_value("length_unit")
        self.info.delete_column(["intensity"])
        self.info.add_column(
            0, "pt_no", "int32", "num", "Point number")
        self.info.add_column(
            0, "x_" + length_unit, "float32", length_unit, "X-coordinate")
        self.info.add_column(
            0, "y_" + length_unit, "float32", length_unit, "Y-coordinate")
        self.info.add_column(
            0, "intensity", "float32", "a.u.", "Pixel intensity")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Convert nonzero local max pixels to X,Y-coordinate.

        Args:
            reqs[0] (numpy.ndarray): Numpy 3D array with the shape of
                (1, height, width).
            param["length_unit"] (str): Unit string for column names such as
                "um" and "nm".
            param["pitch"] (float): Length per pixel.

        Returns:
            pandas.DataFrame: X,Y-coordinate of local max pixels

        """
        img = reqs[0].copy()
        if img.shape[0] != 1:
            raise Exception(
                "Input image should be split into a single frame image.")
        frm = img[0, :, :]
        yxi = find(csr_matrix(frm))
        df = pd.DataFrame(
            {"pt_no": range(1, len(yxi[0]) + 1),
                "x_" + param["length_unit"]: yxi[1] * param["pitch"],
                "y_" + param["length_unit"]: yxi[0] * param["pitch"],
                "intensity": yxi[2]})
        return df

    def post_run(self):
        """Index columns should be added on the upper level of the DataFrame.
        """
        merge_different_index(self, 0)


class LocalMax2XyWithDoG(Table):
    """Convert nonzero local max pixels to X,Y-coordinate with DoG filter.

    Args:
        reqs[0] (Image): Image to apply the filter to. Required parameters;
            ``length_unit``, ``pitch``.
        param["wavelength"] (int): Emission wavelength in length_unit.
        param["NA"] (float): Numerical aperture.
        param["size_factor"] (float, optional): Particle size factor to
            multiply PSF size. Defaults to 1.
        param["mask_factor"] (float, optional): Mask size factor to multiply
            PSF diameter. Defaults to 1.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: X,Y-coordinate of detected local max
    """

    def set_info(self, param):
        """Copy info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        length_unit = self.info.get_param_value("length_unit")
        self.info.delete_column(["intensity"])
        self.info.add_column(
            0, "pt_no", "int32", "num", "Point number")
        self.info.add_column(
            0, "x_" + length_unit, "float32", length_unit, "X-coordinate")
        self.info.add_column(
            0, "y_" + length_unit, "float32", length_unit, "Y-coordinate")
        self.info.add_column(
            0, "intensity", "float32", "a.u.", "Pixel intensity")

        pitch = self.info.get_param_value("pitch")
        d_psf_pix = (1.22 * param["wavelength"] / (param["NA"] * pitch))

        self.info.add_param(
            "d_psf", d_psf_pix, "pix", "PSF diameter")
        self.info.add_param(
            "wavelength", param["wavelength"], length_unit, "Wavelength")
        self.info.add_param(
            "NA", param["NA"], "none", "Numerical aperture")
        if "size_factor" not in param:
            param["size_factor"] = 1
        self.info.add_param(
            "size_factor", param["size_factor"], "none",
            "Particle size factor to multiply PSF size")

        particle_size = param["size_factor"] * d_psf_pix

        dog_sd1 = particle_size / (1 + np.sqrt(2))
        dog_sd2 = np.sqrt(2) * dog_sd1
        self.info.add_param(
            "dog_sd1", dog_sd1, "pix", "SD of Gauss filter 1")
        self.info.add_param(
            "dog_sd2", dog_sd2, "pix", "SD of Gauss filter 2")
        if "mask_factor" not in param:
            param["mask_factor"] = 1
        self.info.add_param(
            "mask_factor", param["mask_factor"], "none",
            "Local maximum mask size factor")
        mask_size = int(np.ceil(param["mask_factor"] * d_psf_pix))
        self.info.add_param(
            "mask_size", mask_size, "pix", "Local maximum mask size")

        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Convert nonzero local max pixels to X,Y-coordinate with DoG filter.

        Args:
            reqs[0] (numpy.ndarray): Image to apply the filter to. The image
                should have the shape of (frame number, height, width).
            param["dog_sd1"] (float): Standard deviation of the first Gaussian
                filter.
            param["dog_sd2"] (float): Standard deviation of the second Gaussian
                filter.
            param["mask_size"] (int): Mask size factor to multiply PSF
                diameter.
            param["length_unit"] (str): Unit string for column names such as
                "um" and "nm".
            param["pitch"] (float): Length per pixel.

        Returns:
            pandas.DataFrame: X,Y-coordinate of local max pixels
        """
        img = reqs[0].copy()
        img = DifferenceOfGaussian.process(reqs, param)
        img = LocalMax.process([img], param)
        df = LocalMax2Xy.process([img], param)
        return df

    def post_run(self):
        """Index columns should be added on the upper level of the DataFrame.
        """
        merge_different_index(self, 0)
