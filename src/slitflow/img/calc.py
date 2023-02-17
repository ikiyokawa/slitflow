import numpy as np
import pandas as pd
from ..tbl.table import Table, merge_different_index
from .. import setindex


class MaskArea(Table):
    """Calculate mask area by counting non-zero pixel number in an image.

    Args:
        reqs[0] (Image): Image stack to calculate area. Required param;
            ``length_unit``, ``pitch``.
        param["split_depth"] (int): File split depth number.

    Returns:
        Table: Area Table
    """

    def set_index(self):
        """Copy index from the required data index."""
        setindex.from_req(self, 0)

    def set_info(self, param={}):
        """Copy index information from reqs[0] and add area column."""
        self.info.copy_req(0)
        self.info.delete_column(keeps=self.info.get_column_name("index"))
        length_unit = self.info.get_param_value("length_unit")
        self.info.add_column(
            0, "area", "float", length_unit + "^2", "Area size of mask image")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Calculate mask area by counting non-zero pixel number in an image.

        Args:
            reqs[0] (numpy.ndarray): Image stack to calculate area.
            param["pitch"] (int): Length per pixel in length_unit.

        Returns:
            pandas.DataFrame: Area table
        """
        img = reqs[0].copy()
        areas = []
        for i in range(img.shape[0]):
            areas.append(np.count_nonzero(img[i, :, :]))
        return pd.DataFrame({"area": np.array(areas) * param["pitch"]**2})

    def post_run(self):
        """Merge the index table to the split result data."""
        merge_different_index(self, 0)
