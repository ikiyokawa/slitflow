import numpy as np

from ..tbl.table import Table


class CutOffPixelQuantile(Table):
    """Select table rows by the intensity count quantile.

    Noise distribution seems to be Gaussian distribution. However, the
    image includes signals and results in gamma-like distribution. This
    function uses Median + factor * (Q2 - Q1) as intensity threshold
    instead of Mean + factor * STD to avoid using signal-biased STD.

    .. caution::

        The threshold is calculated from all rows entered into the
        :meth:`process`. You have to split the required data into appropriate
        depths.

    Args:
        reqs[0] (Table): Table including intensity values.
        param["calc_col"] (str): Column name for calculating the median.
        param["cut_factor"] (float): Cutoff factor above the median value.
        param["ignore_zero"] (bool, optional): Whether zero values are ignored
            from the intensity.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Selected Table
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] and add params.
        """
        self.info.copy_req(0)
        self.info.add_param(
            "cut_factor", param["cut_factor"], "num", "Quantile factor")
        self.info.add_param(
            "calc_col", param["calc_col"], "str",
            "Column name for calculating median")

        if ("ignore_zero", True) in param.items():
            self.info.add_param(
                "ignore_zero", param["ignore_zero"], "bool",
                "Whether zero values are ignored from the intensity")

        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Select table rows by the intensity count quantile.

        Args:
            reqs[0] (pandas.DataFrame): Table including intensity values.
            param["calc_col"] (str): Column name for calculating the median.
            param["cut_factor"] (float): Cutoff factor above the median value.
            param["ignore_zero"] (bool, optional): Whether zero values are
                ignored from the intensity.

        Returns:
            pandas.DataFrame: Selected table
        """
        df = reqs[0].copy()
        intensity = df[param["calc_col"]].values
        if ("ignore_zero", True) in param.items():
            intensity = intensity[np.nonzero(intensity)]
        pct = np.percentile(intensity, q=[25, 50])
        dif_q = pct[1] - pct[0]
        threshold = pct[1] + dif_q * param["cut_factor"]
        return df[df[param["calc_col"]] > threshold]
