import numpy as np

from ..img.image import Image, RGB
from .. import RANDOM_SEED

np.random.seed(RANDOM_SEED)


class Black(Image):
    """Create black image using Index table.

    Args:
        reqs[0] (Table): Index table.
        param["pitch"] (float): Pixel size in length_unit/pix.
        param["interval"] (float, optional): Time interval (s).
        param["img_size"] (list of int): Width and height of each image (pix).
        param["length_unit"] (str): Unit string for column names such as "um",
            "nm", "pix".
        param["split_depth"] (int): File split depth.

    Returns:
        Image: Black Image
    """

    def set_info(self, param={}):
        self.info.copy_req()
        self.info.add_param("pitch", param["pitch"], param["length_unit"]
                            + "/pix", "Pixel size")
        if "interval" in param:
            self.info.add_param("interval", param["interval"], "s/frame",
                                "Time interval")
        self.info.add_column(0, "intensity", "uint8",
                                "a.u.", "Pixel intensity")
        self.info.add_param("img_size", param["img_size"], "pix",
                            "Width and height of each image")
        self.info.add_param("length_unit", param["length_unit"],
                            "str", "Unit of length")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Create black image using Index table.

        Args:
            reqs[0] (pandas.DataFrame): Index table.
            param["img_size"] (list of int): Width and height of each image
                (pix).

        Returns:
            numpy.ndarray: Black image
        """
        df = reqs[0].copy()
        return np.zeros([len(df), param["img_size"][1],
                         param["img_size"][0]])


class RandomRGB(RGB):
    """Create random RGB image using Index table.

    Args:
        reqs[0] (Table): Index table.
        param["pitch"] (float): Pitch size with unit/pix.
        param["interval"] (float, optional): Time interval (s).
        param["img_size"] (list of int): Width and height of each image (pix).
        param["split_depth"] (int): File split depth.
        param["length_unit"] (str): Unit string for column names such as "um",
            "nm", "pix".
        param["seed"] (int, optional): Random seed.

    Returns:
        Image: RGB Image
    """

    def set_info(self, param={}):
        self.info.copy_req()
        self.info.add_param("pitch", param["pitch"], param["length_unit"]
                            + "/pix", "Pixel size")
        if "interval" in param:
            self.info.add_param("interval", param["interval"], "s/frame",
                                "Time interval")
        self.info.add_column(0, "intensity", "uint8",
                                "a.u.", "Pixel intensity")
        self.info.add_param("img_size", param["img_size"], "pix",
                            "Width and height of each image")
        self.info.add_param("length_unit", param["length_unit"],
                            "str", "Unit of length")
        index_counts = self.reqs[0].info.get_param_value("index_counts")
        index_counts.append(3)
        self.info.add_param("index_counts", index_counts,
                            "list of int",
                            "Index counts including the color number")
        if "seed" in param:
            self.info.add_param("seed", param["seed"], "int", "Random seed")
            np.random.seed(param["seed"])
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Create random RGB image.

        Args:
            reqs[0] (pandas.DataFrame): Index table.
            param["img_size"] (list of int): Width and height of each image
                (pix).
            param["index_counts"] (list of int): Index counts ending with 3,
                the color number.

        Returns:
            numpy.ndarray: RGB image
        """
        n_img = np.prod(param["index_counts"])
        return np.random.randint(0, 255, [n_img, param["img_size"][0],
                                          param["img_size"][1]])
