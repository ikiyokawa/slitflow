import numpy as np

from ..img.image import Image
from ..fun.misc import reduce_list as rl


class Gauss2D(Image):
    """Plot Gaussian spots according to X,Y-coordinate.

    .. caution::

        Trajectory data should be converted to localization data.

    Args:
        reqs[0] (Table): Localization data including X,Y-coordinate columns.
            Required param; ``length_unit``.
        param["pitch"] (float): Length per pixel of reconstructed image.
        param["sd"] (float): Standard deviation of Gaussian spots.
        param["img_size] (list of int): Image size as [width, height] pixels.
        param["window_factor"] (float): S.D. of Gaussian spots is multiplied by
            this factor for the half pixel width of rendering clip of Gaussian
            spots. If you set a too small value, Gaussian spots will be
            truncated square-shaped spots.
        param["group_depth"] (int): Plots grouping depth. The grouped
            coordinates by this depth will be plotted into the same frame.
        param["split_depth"] (int): File split depth number.

    Returns:
        Image: Image class of reconstructed ``float32`` tiff file
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and modify columns and add params.
        """
        self.info.copy_req(0)
        length_unit = self.info.get_param_value("length_unit")
        self.info.set_group_depth(param["group_depth"])
        self.info.delete_column(keeps=self.info.get_param_value("index_cols"))
        self.info.add_column(
            0, "intensity", "float32", "a.u.", "Pixel intensity")
        self.info.add_param(
            "calc_cols", ["x_" + length_unit, "y_" + length_unit],
            "list of str", "X,Y-coordinate columns")
        self.info.add_param(
            "pitch", param["pitch"], length_unit + "/pix",
            "Length per pixel of reconstructed image")
        self.info.add_param(
            "img_size", param["img_size"], "pix",
            "Image size as [width, height] pixels")
        self.info.add_param(
            "sd", param["sd"], length_unit, "Standard deviation of Gauss plot")
        self.info.add_param(
            "window_factor", param["window_factor"],
            "float", "Multiplying factor of plot S.D. for half window width")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Plot Gaussian spots according to X,Y-coordinate.

        Args:
            reqs[0] (pandas.DataFrame): Localization data including
                X,Y-coordinate columns.
            param["calc_cols"] (list of str): X,Y-coordinate columns.
            param["pitch"] (float): Length per pixel of reconstructed image.
            param["sd"] (float): Standard deviation of Gaussian spots.
            param["img_size] (list of int): Image size as [width, height]
                pixels.
            param["window_factor"] (float): S.D. of Gaussian spots is 
                multiplied by this factor for the half pixel width of rendering
                clip of Gaussian spots. If you set a too small value, Gaussian
                spots will be truncated square-shaped spots.
            param["index_cols"] (list of str): Column names of index.

        Returns:
            numpy.ndarray: Reconstructed image stack
        """

        df = reqs[0].copy()
        width_unit = param["img_size"][0]
        width = np.floor(width_unit).astype(np.int32)
        height_unit = param["img_size"][1]
        height = np.floor(height_unit).astype(np.int32)

        grouped = df.groupby(rl(param["index_cols"]))
        img = []
        for _, df_group in grouped:
            xcs = df_group[param["calc_cols"][0]].values / param["pitch"]
            ycs = df_group[param["calc_cols"][1]].values / param["pitch"]

            frm = np.zeros([height, width])
            sd = param["sd"] / param["pitch"]
            window = np.ceil(sd * param["window_factor"])
            x_pix = np.arange(0.5, 2 * window + 1, 1.0)
            y_pix = np.arange(0.5, 2 * window + 1, 1.0)
            x_grid, y_grid = np.meshgrid(x_pix, y_pix)
            for xc, yc in zip(xcs, ycs):
                yc = width - yc
                dx = xc - np.floor(xc)
                left = (xc - dx - window).astype(int)
                right = (xc - dx + window + 1).astype(int)
                dy = yc - np.floor(yc)
                top = (yc - dy - window).astype(int)
                bottom = (yc - dy + window + 1).astype(int)
                if np.all([0 <= left, right <= width, 0 <= top, bottom
                           <= width]):
                    add_vals = gauss2d(
                        x_grid, y_grid, window + dx, window + dy, sd)
                    frm[top:bottom, left:right] = \
                        frm[top:bottom, left:right] + add_vals
            frm = np.flipud(frm)
            img.append(frm)
        return np.array(img)


def gauss2d(x, y, xc, yc, s):
    """Equation for plotting 2D Gaussian image.

    Args:
        x (float): X-coordinate of grid position.
        y (float): Y-coordinate of grid position.
        xc (float): X center of Gaussian distribution.
        yc (float): Y center of Gaussian distribution.
        s (float): Standard deviation of Gaussian distribution.

    Returns:
        float: Gaussian value of (x, y)
    """
    return 1. / (2. * np.pi * s**2) * np.exp(-((x - xc)**2. + (y - yc)**2.) /
                                             (2. * s**2.))
