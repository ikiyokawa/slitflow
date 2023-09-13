import numpy as np
import pandas as pd
from ..img.image import Image, RGB, set_color_index


class Obs2Depth(Image):
    """Merge images from different observations into the top level depth.

    .. caution::

        This class only works when used in a Pipeline object. Running the
        process method or creating a Data object does not work appropriately.

    Observation names for merging should be listed into ``obs_name`` argument
    of :meth:`~slitflow.manager.Pipeline.add` in Pipeline class.

    Args:
        reqs (list of Image): Images for merge.
        param["col_name"] (str, optional): New column name for observation
            numbers. Defaults to "obs_no".
        param["col_description"] (str, optional): New column description.
            Defaults to "Observation number".
        param["obs_name"] (str): New observation name.
        param["split_depth"] (int): File split depth number.

    Returns:
        Image: Merged Image
    """

    def set_index(self):
        """Add observation number to the top level of index columns.
        """
        indices = []
        pcol_name = self.info.get_column_name()[0]
        for i, req in enumerate(self.reqs):
            index = req.info.file_index().copy()
            if len(index) == 0:
                index = pd.DataFrame({pcol_name: [i + 1]}).astype(int)
            else:
                index.insert(0, pcol_name, i + 1)
            indices.append(index)
        self.info.index = pd.concat(indices).reset_index(drop=True)
        self.info.set_index_file_no()

    def set_info(self, param={}):
        """Copy info from reqs[0] and add columns and params.
        """
        self.info.copy_req(0)
        if "col_name" not in param:
            param["col_name"] = "obs_no"
            param["col_description"] = "Observation number"
        self.info.add_column(
            1, param["col_name"], "int32", "num", param["col_description"])
        self.info.add_param(
            "obs_name", param["obs_name"], "str", "New observation name")
        self.info.add_param(
            "col_name", param["col_name"], "str", "New column name")

        # This parameter is saved from Pipeline.run_Obs2Depth()
        self.info.add_param(
            "merged_obs_names", param["merged_obs_names"], "list of str",
            "Merged observation names for correspondence of numbers and\
                names")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Merge images from different observations into the top level depth.

        Args:
            reqs (list of numpy.ndarray): Images from different
                observations.

        Returns:
            numpy.ndarray: Merged image
        """
        return np.concatenate(reqs, axis=0)


class Obs2DepthRGB(RGB):
    """Merge RGB images from different observations into the top level depth.

    .. caution::

        This class only works when used in a Pipeline object. Running the
        process method or creating a Data object does not work appropriately.

    Observation names for merging should be listed into ``obs_name`` argument
    of :meth:`~slitflow.manager.Pipeline.add` in Pipeline class.

    Args:
        reqs (list of ~slitflow.img.image.RGB): RGB Images for merge.
        param["col_name"] (str, optional): New column name for observation
            numbers. Defaults to "obs_no".
        param["col_description"] (str, optional): New column description.
            Defaults to "Observation number".
        param["obs_name"] (str): New observation name.
        param["split_depth"] (int): File split depth number.

    Returns:
        slitflow.img.image.RGB: Merged RGB image
    """

    def set_index(self):
        """Add observation number to the top-level of index columns.
        """
        indices = []
        pcol_name = self.info.get_column_name()[0]
        for i, req in enumerate(self.reqs):
            index = req.info.file_index().copy()
            index.insert(0, pcol_name, i + 1)
            indices.append(index)
        self.info.index = pd.concat(indices).reset_index(drop=True)
        self.info.set_index_file_no()

    def set_info(self, param={}):
        """Copy info from reqs[0] and add columns and params.
        """
        self.info.copy_req(0)
        if "col_name" not in param:
            param["col_name"] = "obs_no"
            param["col_description"] = "Observation number"
        self.info.add_column(
            1, param["col_name"], "int32", "num", param["col_description"])
        self.info.add_param(
            "obs_name", param["obs_name"], "str", "New observation name")
        self.info.add_param(
            "col_name", param["col_name"], "str", "New column name")

        # This parameter is saved from Pipeline.run_Obs2Depth()
        self.info.add_param(
            "merged_obs_names", param["merged_obs_names"], "list of str",
            "Merged observation names for correspondence of numbers and\
                names")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Merge RGB images from different observations to the top level depth.

        Args:
            reqs (list of numpy.ndarray): RGB images from different
                observations.

        Returns:
            numpy.ndarray: Merged RGB image
        """
        return np.concatenate(reqs, axis=0)
