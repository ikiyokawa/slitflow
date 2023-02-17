"""
Classes in this module return filtered images with the same shape as the
required image.
"""
import importlib  # skimage

import numpy as np
import cv2
import scipy

from ..img.image import Image


class Gauss(Image):
    """Apply Gaussian filter to images using cv2.GaussBlur.

    Args:
        reqs[0] (Image): Image stack.
        param["kernel_size"] (odd integer): GaussianBlur kernel size.
        param["split_depth"] (int): File split depth number.

    Return:
        Image: Filtered Image
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        self.info.add_param("kernel_size", param["kernel_size"], "int",
                            "GaussianBlur kernel size must be odd.")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Apply Gaussian filter to images using cv2.GaussBlur.

        Args:
            reqs[0] (numpy.ndarray): Numpy 3D array with the shape of
                (frame number, height, width).
            param["kernel_size"] (odd integer): GaussianBlur kernel size.

        Returns:
            numpy.ndarray: Filtered image array
        """
        img = reqs[0].copy()
        for i in range(img.shape[0]):
            x = img[i, :, :]
            img[i, :, :] = cv2.GaussianBlur(x, (param["kernel_size"],
                                                param["kernel_size"]), 0)
        return img


class DifferenceOfGaussian(Image):
    """Apply the Difference of Gaussian filter for particle detection.

    This filter follows the strategy of TrackMate, where sigma_1 and sigma_2
    of the DoG filter are determined from the particle diameter.
    See also `trackmate algorithms
    <https://imagej.net/plugins/trackmate/algorithms>`_ .

    In this class, the particle diameter is set to the size of the Airy disc,

    d_psf = (1.22 * wavelength / NA) / pitch.

    You can adjust the particle size by multiplying it with ``size_factor``.
    The ``wavelength`` parameter should have the same unit with
    ``length_unit``.


    Args:
        reqs[0] (Image): Image to apply the filter to. Required parameters;
            ``length_unit``, ``pitch``.
        param["wavelength"] (int): Emission wavelength in length_unit.
        param["NA"] (float): Numerical aperture.
        param["size_factor"] (float, optional): Particle size factor to
            multiply PSF size. Defaults to 1.
        param["split_depth"] (int): File split depth number.

    Returns:
        Image: Filtered image object in ``float32``
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        length_unit = self.info.get_param_value("length_unit")
        col = self.info.get_column_dict("intensity")
        self.info.delete_column(["intensity"])
        self.info.add_column(
            col["depth"], col["name"], "float32", col["unit"],
            col["description"])

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
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Apply the Difference of Gaussian filter for particle detection.

        Args:
            reqs[0] (numpy.ndarray): Image to apply the DoG filter to. The
                image should have the shape of (frame number, height, width).
            param["dog_sd1"] (float): Standard deviation of the first Gaussian
                filter.
            param["dog_sd2"] (float): Standard deviation of the second Gaussian
                filter.

        Returns:
            numpy.ndarray: Filtered image
        """
        img = reqs[0].copy().astype(np.float32)
        for i in range(img.shape[0]):
            frm = img[i, :, :]
            blur1 = scipy.ndimage.gaussian_filter(frm, param["dog_sd1"])
            blur2 = scipy.ndimage.gaussian_filter(frm, param["dog_sd2"])
            img[i, :, :] = blur1 - blur2
        return img


class LocalMax(Image):
    """Local maximum filter for particle images.

    Get local maximum values by using maximum_filter in SciPy. Surrounding
    pixel values except local maximum are set to 0.

    Args:
        reqs[0] (DifferenceOfGaussian): DoG filtered Image to apply this
            filter to. Required params; ``d_psf``.
        param["mask_factor"] (float, optional): Mask size factor to multiply
            PSF diameter. Defaults to 1.
        param["split_depth"] (int): File split depth number.

    Returns:
        Image: Filtered image object
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        d_psf = self.info.get_param_value("d_psf")
        if "mask_factor" not in param:
            param["mask_factor"] = 1
        self.info.add_param(
            "mask_factor", param["mask_factor"], "none",
            "Local maximum mask size factor")
        mask_size = int(np.ceil(param["mask_factor"] * d_psf))
        self.info.add_param(
            "mask_size", mask_size, "pix", "Local maximum mask size")

        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Local maximum filter for particle images.

        Args:
            reqs[0] (numpy.ndarray): DoG filtered Image to apply the
                local maximum filter to. The image should have the shape of
                (frame number, height, width).
            param["mask_size"] (int): Mask size factor to multiply PSF
                diameter.

        Returns:
            numpy.ndarray: Filtered image
        """
        skimage = importlib.import_module("skimage")
        img = reqs[0].copy().astype(np.float32)
        for i in range(img.shape[0]):
            frm = img[i, :, :]
            max_img = scipy.ndimage.maximum_filter(
                frm, footprint=skimage.morphology.disk(param["mask_size"]))
            max_img[np.logical_not(max_img == frm)] = 0
            img[i, :, :] = max_img
        return img


class LocalMaxWithDoG(Image):
    """Local max image for particle detection with the Difference of Gaussian.

    This class is the combination of
    :class:`~slitflow.img.filter.DifferenceOfGaussian` and
    :class:`~slitflow.img.filter.LocalMax`.

    You can use this class to skip exporting the result of DifferenceOfGaussian
    .

    Args:
        reqs[0] (Image): Image to apply the filter to. Required parameters;
            ``length_unit``, ``pitch``.
        param["wavelength"] (int): Emission wavelength in length_unit.
        param["NA"] (float): Numerical aperture.
        param["size_factor"] (float, optional): Particle size factor to
            multiply PSF size. Defaults to 1.
        param["mask_factor"] (float): Mask size factor to multiply PSF
            diameter. Defaults to 1.
        param["split_depth"] (int): File split depth number.

    Returns:
        Image: Filtered image object
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        length_unit = self.info.get_param_value("length_unit")
        col = self.info.get_column_dict("intensity")
        self.info.delete_column(["intensity"])
        self.info.add_column(
            col["depth"], col["name"], "float32", col["unit"],
            col["description"])

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

    @staticmethod
    def process(reqs, param):
        """Local max image for particle detection with the DoG filtering.

        Args:
            reqs[0] (numpy.ndarray): Image to apply the filter to. The image
                should have the shape of (frame number, height, width).
            param["dog_sd1"] (float): Standard deviation of the first Gaussian
                filter.
            param["dog_sd2"] (float): Standard deviation of the second Gaussian
                filter.
            param["mask_size"] (int): Mask size factor to multiply PSF
                diameter.

        Returns:
            numpy.ndarray: Filtered image
        """
        img = DifferenceOfGaussian.process(reqs, param)
        img = LocalMax.process([img], param)
        return img
