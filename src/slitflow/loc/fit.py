import numpy as np
import pandas as pd
from scipy.optimize import curve_fit, OptimizeWarning

from ..tbl.table import Table

import warnings
warnings.simplefilter("ignore", RuntimeWarning)


class Gauss2D(Table):
    """Fit spot localizations with 2D Gaussian distribution.

    .. caution::

        The input image should be split into a single frame image. In other
        words, the shape of reqs[0] in :meth:`process` should be (1, height,
        width).

    Args:
        reqs[0] (Image): Image to fit. Required params; ``pitch``,
            ``length_unit``.
        reqs[1] (Table): Roughly predicted X,Y-coordinate.
        param["half_width"] (int): Half width of the clipping rectangle in
            pixel to fit the spot image. The shape of clipped image is
            (2 * half_width + 1, 2 * half_width + 1).
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Refined X,Y-coordinate
    """

    def set_info(self, param={}):
        """Copy params from reqs[0] and columns from reqs[1].
        """
        self.info.copy_req(0, "param")
        length_unit = self.info.get_param_value("length_unit")
        calc_cols = ["x_" + length_unit, "y_" + length_unit]
        index = self.reqs[1].info.get_column_name("index") + calc_cols
        self.info.copy_req_columns(1, index)
        self.info.add_column(
            0, "amp", "float64", "a.u.", "Amplitude")
        self.info.add_column(
            0, "sigma", "float64", length_unit,
            "Standard deviation of fitted 2D Gaussian")
        self.info.add_column(
            0, "back", "float64", "a.u.", "Background offset")
        self.info.add_column(
            0, "amp_se", "float64", "a.u.", "Standard error of amplitude")
        self.info.add_column(
            0, "se_x", "float64", length_unit,
            "Standard error of X-coordinate")
        self.info.add_column(
            0, "se_y", "float64", length_unit,
            "Standard error of Y-coordinate")
        self.info.add_column(
            0, "se_sigma", "float64", length_unit,
            "Standard error of 2D Gaussian sigma")
        self.info.add_column(
            0, "se_back", "float64", "a.u.", "Standard error of background")
        self.info.add_column(
            0, "rmsr", "float64", "none",
            "Root mean square of residual (Background)")
        self.info.add_column(
            0, "rsqr", "float64", "none", "R-squared")
        self.info.add_param(
            "use_cols", index, "list of str", "Column names to use")
        self.info.add_param(
            "calc_cols", calc_cols, "list of str", "Calculation column names")
        self.info.add_param(
            "half_width", param["half_width"], "int",
            "Half width of the clipping rectangle")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Fit spot localizations with 2D Gaussian distribution.

        Args:
            reqs[0] (numpy.ndarray): Numpy 3D array with the shape of
                (1, height, width).
            reqs[1] (pandas.DataFrame): Roughly predicted X,Y-coordinate.
            param["calc_cols"] (list of str): X,Y-coordinate column names.
            param["use_cols"] (list of str): Column names to use. Index column
                names + calc_cols.
            param["half_width"] (int): Half width of the clipping rectangle in
                pixel to fit the spot image. The shape of clipped image is
                (2 * half_width + 1, 2 * half_width + 1).
            param["split_depth"] (int): File split depth number.

        Returns:
            Table: Refined X,Y-coordinate
        """
        img = reqs[0].copy()
        df = reqs[1].copy()
        df = df[param["use_cols"]]
        if img.shape[0] != 1:
            raise Exception(
                "Input image should be split into a single frame image.")
        frm = img[0, :, :]
        xs_ref = df[param["calc_cols"][0]].values
        ys_ref = df[param["calc_cols"][1]].values

        xs_ref = xs_ref / param["pitch"]
        ys_ref = ys_ref / param["pitch"]

        vals = np.empty((0, 12), np.float64)
        for x_ref, y_ref in zip(xs_ref, ys_ref):
            x_raw_pos = int(np.floor(x_ref))
            y_raw_pos = int(np.floor(y_ref))

            clip_left = x_raw_pos - param["half_width"]
            clip_right = x_raw_pos + param["half_width"] + 1
            clip_bottom = y_raw_pos - param["half_width"]
            clip_top = y_raw_pos + param["half_width"] + 1

            to_x = (0 <= clip_left) & (clip_right <= frm.shape[1])
            to_y = (0 <= clip_bottom) & (clip_top <= frm.shape[0])
            if to_x & to_y:
                clip = frm[clip_bottom:clip_top,
                           clip_left:clip_right]
                res = np.array(fit_gauss_2d(clip, param["half_width"]))
                x_fit = res[2] + 0.5 + x_raw_pos - param["half_width"]
                y_fit = res[1] + 0.5 + y_raw_pos - param["half_width"]
                res[2] = x_fit
                res[1] = y_fit
                vals = np.append(vals, [res], axis=0)
            else:
                vals = np.append(vals, [np.zeros(12)], axis=0)
        vals = vals.T

        vals[1] = vals[1] * param["pitch"]
        vals[2] = vals[2] * param["pitch"]
        vals[3] = vals[3] * param["pitch"]
        vals[6] = vals[6] * param["pitch"]
        vals[7] = vals[7] * param["pitch"]
        vals[8] = vals[8] * param["pitch"]

        df_val = pd.DataFrame(
            {param["calc_cols"][0]: vals[2],
             param["calc_cols"][1]: vals[1], "amp": vals[0],
             "sigma": vals[3], "back": vals[4], "se_amp": vals[5],
             "se_x": vals[7], "se_y": vals[6], "se_sigma": vals[8],
             "se_back": vals[9], "rmsr": vals[10], "rsqr": vals[11]})

        df_index = df.drop(param["calc_cols"], axis=1)
        df_index = df_index.reset_index(drop=True)
        df_val = df_val.reset_index(drop=True)
        df_new = pd.concat([df_index, df_val], axis=1)
        return df_new


def fit_gauss_2d(clip, half_width):
    """ Fit clip image with 2D Gaussian.

    Args:
        clip (numpy.ndarray): Two-dimensional array for fitting.
        half_width (int) : Half width of the clipping rectangle.
            clip.shape = (2 * half_width + 1, 2 * half_width + 1).

    Return:
        tuples containing

        - amplitude (float): Amplitude of 2D Gaussian
        - y_center (float): Y-coordinate of 2D Gaussian center
        - x_center (float): X-coordinate of 2D Gaussian center
        - sigma (float): Standard deviation of 2D Gaussian
        - back (float): Background offset of 2D Gaussian
        - se_amplitude (float): Standard deviation error of amplitude
        - se_y_center (float): Standard deviation error of Y-coordinate
        - se_x_center (float): Standard deviation error of X-coordinate
        - se_sigma (float): Standard deviation error of sigma
        - se_back (float): Standard deviation error of background
        - rmsr (float): Root mean square of residual (Background)
        - rsqr (float): R-squared

        If fitting is failed, this function returns (amp_ini, half_width,
        half_width, half_width / 3, back_ini, 100, 100, 100, 100, 100, 1, 1)

    """
    edge = clip.copy().astype(np.float64)
    edge[1: -1, 1: -1] = np.Inf
    back_ini = edge[np.logical_not(edge == np.Inf)].mean()
    amp_ini = (clip.copy() - back_ini).sum()
    initial_guess = (amp_ini, half_width, half_width, half_width / 3, back_ini)
    try:
        popt, pcov = curve_fit(
            gauss2d, np.indices(clip.shape), clip.ravel(), p0=initial_guess,
            bounds=((0, 0, 0, 0, 0),
                    (amp_ini * 10, half_width * 2 + 1, half_width * 2 + 1,
                     half_width, back_ini * 3)))
    except (ValueError, RuntimeError, OptimizeWarning):
        replaced = [amp_ini, half_width, half_width,
                    half_width / 3, back_ini, 100, 100, 100, 100, 100, 1, 1]
        return tuple(replaced)

    residuals = clip.ravel() - gauss2d(np.indices(clip.shape), *popt)
    rss = np.sum(residuals**2)
    rmsr = np.sqrt(rss / (len(residuals) - 2))
    tss = np.sum((clip.ravel() - np.mean(clip.ravel()))**2)
    rsqr = 1 - (rss / tss)
    sde = np.sqrt(np.diag(pcov))

    return *popt, *sde, rmsr, rsqr


def gauss2d(xy, amp, xc, yc, sigma, back):
    """Returns the 2D Gaussian value of the X,Y-coordinate.

    Args:
        xy (tuple of float): (x,y) coordinates to calculate the value.
        amp (float): Amplitude.
        xc (float): X-coordinate of 2D Gaussian center.
        yc (float): Y-coordinate of 2D Gaussian center.
        sigma (float): Standard deviation of 2D Gaussian.
        back (float): Background offset of 2D Gaussian.

    Returns:
        float: 2D Gaussian value of the X,Y-coordinate
    """
    (x, y) = xy
    xc = float(xc)
    yc = float(yc)
    g = back + (amp / (2 * np.pi * sigma**2)) * \
        np.exp(-(((x - xc)**2) + (y - yc)**2) / (2 * sigma**2))
    return g.ravel()
