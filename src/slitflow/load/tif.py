import numpy as np
import pandas as pd
import tifffile as tf

from ..img.image import Image


class SingleFile(Image):
    """Import a tiff image as the top level of the observation data.

    Args:
        reqs[] (None): Input Data is not required.
        param["path"] (str): Path to a tiff file.
        param["length_unit"] (str): String of length unit such as "um",
            "nm", "pix". This string is used as column name footers and units.
        param["pitch"] (float, optional): Pixel size in length_unit/pix.
        param["interval"] (float, optional): Time interval.
        param["index_cols"] (list of list, optional): Column names of indexes.
            Each list should have [depth number, column name, description].
            Defaults to [[1, "img_no","Image number"]].
        param["img_nums"] (list of int, optional): Set if image numbers are not
            [1,2,3,...,total_images].
        param["value_type"] (str): Value type of each pixel. "uint8", "uint16"
            or "float32".
        param["split_depth"] (int): File split depth number.

    Returns:
        Image: Tiff Image class

    Examples:
        Import a tiff stack as an observation file.

        .. code-block:: python

            PL = sf.manager.Pipeline(project_directory)
            path = os.path.join(
                image_directory, "image.tif")
            PL.add(sf.load.tif.SingleFile(), 0, (1, 1), "group1", "raw",
                ["Sample1"], [], [],
                {"path": path, "length_unit": "um", "pitch": 0.1,
                    "value_type": "uint16", "split_depth": 0})
            PL.run()
            # image_directory/image.tif
            # is saved as
            # project_directory/g1_group1/a1_raw/
            #    - Sample1_raw.tif
            # with - Sample1.sf, Sample1.sfx
    """

    def set_info(self, param):
        """Create information.
        """
        load_param = get_param(param["path"])
        if "index_cols" not in param:
            param["index_cols"] = [[1, "img_no", "Image number"]]
        for index_col in param["index_cols"]:
            self.info.add_column(
                index_col[0], index_col[1], "int32", "num", index_col[2])
        self.info.add_column(
            0, "intensity", param["value_type"], "a.u.", "Pixel intensity")
        self.info.add_param(
            "length_unit", param["length_unit"], "str", "Unit of length")
        if "pitch" in param:
            self.info.add_param(
                "pitch", param["pitch"], param["length_unit"] + "/pix",
                "Length per pixel")
        self.info.add_param(
            "img_size", [int(load_param["ImgWidth"]), int(
                load_param["ImgHeight"])], "pix", "[width, height] of image")
        if "interval" in param:
            self.info.add_param(
                "interval", param["interval"], "float", "Time interval")
        if "img_nums" not in param:
            param["img_nums"] = np.arange(1, load_param["TotalFrm"] + 1)
        self.info.add_param(
            "_indexes", param["img_nums"], "list of int",
            "Internal parameter of index.")
        self.info.add_param(
            "path", param["path"], "str", "Path to a tiff file")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Load a tiff file from the path string.

        Args:
            param["path"] (str): Tiff file path.

        Returns:
            numpy.ndarray: Image stack array
        """
        path = param["path"]
        with tf.TiffFile(path, mode="r+b") as tif:
            img = tif.pages[0].asarray()
            total_page = len(tif.pages)
            stack = np.zeros([total_page, img.shape[0], img.shape[1]])
            for i in np.arange(0, total_page):
                stack[i, :, :] = np.flipud(tif.pages[i].asarray())
        return stack

    def set_index(self):
        self.info.index = pd.DataFrame(
            np.array(self.info.get_param_value("_indexes")),
            columns=self.info.get_column_name("index"))
        self.info.set_index_file_no()


class SplitFile(Image):
    """Import a tiff image as split image of the observation data.

    Argument names are defined assuming the observation image data that have
    several tiff stacks(img_no=1, 2, ...) that have several frames(frm_no=1, 2,
    ...). If the image size is big, the split_depth should be more than 0 to
    avoid memory over. Path, indexes and frm_nos of last image is saved in the
    info file.

    Args:
        reqs[] (None): Input Data is not required.
        param["path"] (str): Path to a split tiff file.
        param["length_unit"] (str): String of length unit such as "um",
            "nm", "pix". This string is used as column name footers and units.
        param["pitch"] (float): Pixel size in length_unit/pix.
        param["interval"] (float): Time interval between two frames.
        param["index_cols"] (list of list, optional): Column names of indexes.
            Each list should have [depth number, column name, description].
            Defaults to [[1, "img_no", "Image number"], [2, "frm_no", "Frame
            number"]].
        param["indexes"] (list of int): Index numbers of the tiff image. For
            example, if the tiff file is the 3rd image of the observation,
            set [3].
        param["frm_nums"] (list of int, optional): Set if frame numbers are not
            [1, 2, 3, ..., total_frames].
        param["value_type"] (str): Value type of each pixel. "uint8", "uint16"
            or "float32".
        param["split_depth"] (int): File split depth number.

    Returns:
        Image: Tiff Image class

    Examples:
        Import three tiff stacks as the same observation.

        .. code-block:: python

            PL = sf.manager.Pipeline(project_directory)
            for i in [1, 2, 3]:
                path = os.path.join(
                    image_directory, "image-" + str(i) + ".tif")
                PL.add(sf.load.tif.SplitFile(), 0, (1, 1), "group1", "raw",
                    ["Sample1"], [], [],
                    {"path": path, "length_unit": "um", "pitch": 0.1,
                     "value_type": "uint16", "indexes": [i], "split_depth": 1})
            PL.run()
            # image_directory/
            #    - image-1.tif, image-2.tif, image-3.tif
            # is saved as
            # project_directory/g1_group1/a1_raw/
            #    - Sample1_D1_raw.tif, Sample1_D2_raw.tif, Sample1_D3_raw.tif
            # with - Sample1.sf, Sample1.sfx
    """

    def set_info(self, param):
        load_param = get_param(param["path"])
        if "index_cols" not in param:
            param["index_cols"] = [[1, "img_no", "Image number"],
                                   [2, "frm_no", "Frame number"]]
        for index_col in param["index_cols"]:
            self.info.add_column(
                index_col[0], index_col[1], "int32", "num", index_col[2])
        self.info.add_column(
            0, "intensity", param["value_type"], "a.u.", "Pixel intensity")
        self.info.add_param(
            "length_unit", param["length_unit"], "str", "Unit of length")
        self.info.add_param(
            "pitch", param["pitch"], param["length_unit"] + "/pix",
            "Length per pixel")
        if "interval" in param:
            self.info.add_param(
                "interval", param["interval"], "s",
                "Time interval between two frames")
        self.info.add_param(
            "img_size", [int(load_param["ImgWidth"]), int(
                load_param["ImgHeight"])], "pix", "[width, height] of image")
        self.info.add_param(
            "_indexes_fix", param["indexes"], "list of int",
            "Internal param of index")
        if "frm_nums" not in param:
            param["frm_nums"] = np.arange(1, load_param["TotalFrm"] + 1)
        self.info.add_param(
            "_indexes", param["frm_nums"], "list of int",
            "Internal param of index")
        self.info.add_param(
            "path", param["path"], "str", "Path to a split tiff file")
        self.info.set_split_depth(param["split_depth"])

    @ staticmethod
    def process(reqs, param):
        """Load a tiff from the path string.

        See :meth:`SingleFile.process`.

        """
        return SingleFile.process(reqs, param)

    def set_index(self):
        index_fix = np.array(self.info.get_param_value("_indexes_fix"))
        index = np.array(self.info.get_param_value("_indexes"))
        index_fix = np.zeros((index.shape[0], index_fix.shape[0])) + index_fix
        index = np.hstack([index_fix, index[np.newaxis].T]).astype(np.int32)
        self.info.index = pd.DataFrame(
            index, columns=self.info.get_column_name("index"))
        self.info.set_index_file_no()


def get_param(path):
    """Get tiff information.

    Args:
        path (str): Path to a tiff file.

    Returns:
        dict: Dictionary containing TotalFrm, ImgHeight and ImgWidth
    """
    param = {}
    with tf.TiffFile(path) as tif:
        param["TotalFrm"] = len(tif.pages)
        page = tif.pages[0]
        param["ImgHeight"] = page.shape[0]
        param["ImgWidth"] = page.shape[1]
    return param
