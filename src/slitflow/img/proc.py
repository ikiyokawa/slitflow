"""
This process module includes classes that change image structure such as
frm_no and image width and height.
"""
import pandas as pd

from ..img.image import Image
from ..tbl.proc import MaskFromParam


class SelectParam(Image):
    """Select image frames based on parameter values.

    This class creates a mask column based on explicit param values using
    :class:`slitflow.tbl.filter.MaskFromParam` and selects rows using the mask
    column.

    Args:
        reqs[0] (Image): Image for selection.
        reqs[1] (Table): Index Table that includes all indices corresponding to
            the image. The index table should be split into the same depth as
            the image.
        param["index"] (list of tuple): List of image index numbers to select.
            The tuple should be (index of depth=1, index of depth=2, ...).
            If index is None, all indices of the depth is selected.
        param["split_depth"] (int): File split depth number.

    Returns:
        Image: Selected Image.

    Raises:
        Exception: If the split depths of the image and index table are not the
        same.

    """
    _temp_index = []

    def __init__(self, info_path=None):
        super().__init__(info_path)
        SelectParam._temp_index = []

    def set_info(self, param={}):
        """Copy info from reqs[0] and add param."""
        if self.reqs[0].info.split_depth_req != \
                self.reqs[1].info.split_depth_req:
            raise Exception("Split depths should have the same value")
        self.info.copy_req(0)
        self.info.add_param("mask_col", param.get("mask_col", "mask"),
                            "str", "Mask column name")
        self.info.add_param(
            "index", param["index"], "list", "Indices to select")
        self.info.add_param(
            "index_cols", self.info.get_column_name("index"),
            "list", "Index column names")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Select image frames based on parameter values.

        Args:
            reqs[0] (numpy.ndarray): Image for selection.
            reqs[1] (Table): Index Table that includes all indices
                corresponding to the image. The index table should be split
                into the same depth as the image.
            param["index"] (list of tuple): List of tuple of index numbers to
                select. The tuple should be (index of depth=1, index of
                depth=2, ...). If index is None, all indices of the depth is
                selected.
            param["index_cols"] (list of str): The index column names.
            param["mask_col"] (str, optional): The name of the mask column.
                Defaults to "mask".

        Returns:
            Table: Selected Table.
        """

        df_mask = MaskFromParam.process([reqs[1].copy()], param)
        img = reqs[0].copy()
        to_sel = df_mask[param["mask_col"]].values.astype(bool)
        img = img[to_sel, :, :]

        # Save the index (multi-process is not available)
        SelectParam._temp_index.append(df_mask)
        return img

    def set_index(self):
        """Set the index based on the saved temporal index.

        File numbers of the _temp_index are added before selecting the index
        not to skip the numbers that is not selected during saving.

        """
        self.info.index = pd.concat(SelectParam._temp_index)
        self.info.set_index_file_no()
        mask_col = self.info.get_param_value("mask_col")
        self.info.index = self.info.index[self.info.index[mask_col] > 0]
        self.info.index = self.info.index.drop(
            columns=mask_col).drop_duplicates()
