import numpy as np

from ..img.image import Image, RGB
from .noise import Gauss as noise_Gauss
from .. import RANDOM_SEED

np.random.seed(RANDOM_SEED)


class Black(Image):
    """Create black Image using an Index table.

    Args:
        reqs[0] (Table): The Index table.
        param["pitch"] (float): The pixel size in length_unit/pix.
        param["interval"] (float, optional): The time interval in seconds.
        param["img_size"] (list of int): The width and height of each image
            (pixels).
        param["type"] (str, optional): The value type of intensity. Defaults to
            "uint8".
        param["length_unit"] (str): The unit string for image size, such as
            "um", "nm", "pix".
        param["split_depth"] (int): The file split depth number.

    Returns:
        Image: The black image.
    """

    def set_info(self, param={}):
        """Copy info from req[0] and add parameters."""
        self.info.copy_req(0)
        self.info.add_param("pitch", param["pitch"], param["length_unit"]
                            + "/pix", "Pixel size")
        if "interval" in param:
            self.info.add_param("interval", param["interval"], "s/frame",
                                "Time interval")
        if "type" not in param:
            param["type"] = "uint8"
        self.info.add_param("type", param["type"], "str",
                            "Value type of intensity")
        self.info.add_column(
            0, "intensity", param["type"], "a.u.", "Pixel intensity")
        self.info.add_param("img_size", param["img_size"],
                            "pix", "Width and height of each image")
        self.info.add_param("length_unit", param["length_unit"],
                            "str", "Unit of length")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Create black Image using an Index table.

        Args:
            reqs[0] (pandas.DataFrame): The Index table.
            param["img_size"] (list of int): The width and height of each image
                (pixels).

        Returns:
            numpy.ndarray: The black image.
        """
        df = reqs[0].copy()
        return np.zeros([len(df), param["img_size"][1],
                         param["img_size"][0]])


class RandomRGB(RGB):
    """Create random RGB image using Index table.

    Args:
        reqs[0] (Table): Index table.
        param["pitch"] (float): Pitch size in length_unit/pix.
        param["interval"] (float, optional): Time interval in second.
        param["img_size"] (list of int): Width and height of each image in
            pixel.
        param["split_depth"] (int): File split depth number.
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

        Returns:
            numpy.ndarray: RGB image
        """
        df = reqs[0].copy()
        n_img = len(df) * 3
        return np.random.randint(0, 255, [n_img, param["img_size"][0],
                                          param["img_size"][1]])


class CheckerBoard(Image):
    """Create a checkerboard image using an index table.

    Args:
        reqs[0] (Table): The index table.
        param["pitch"] (float): The pixel size in length_unit/pixel.
        param["interval"] (float, optional): The time interval in seconds.
        param["img_size"] (list of int): The width and height of each image in
            pixels.
        param["box_size"] (list of int):  The width and height of each
            checkerboard box in pixels.
        param["type"] (str, optional): The value type of intensity. Defaults to
            "uint8".
        param["length_unit"] (str): The unit string for column names such as
            "um", "nm", or "pix".
        param["intensity" (int or str): The degree of whiteness in each frame.
            If "ascend" is specified, the degree of whiteness increases by one
            in each subsequent frame.
        param["split_depth"] (int): File split depth number.

    Returns:
        Image: Checkerboard image stack.
    """

    def set_info(self, param={}):
        """Set info from reqs[0] and add image parameters."""
        self.info.copy_req(0)
        if "type" not in param:
            param["type"] = "uint8"
        self.info.add_param("type", param["type"], "str",
                            "Value type of intensity")
        self.info.add_column(0, "intensity", param["type"],
                                "a.u.", "Pixel intensity")
        self.info.add_param("pitch", param["pitch"], param["length_unit"]
                            + "/pix", "Pixel size")
        if "interval" in param:
            self.info.add_param("interval", param["interval"], "s/frame",
                                "Time interval")
        self.info.add_param("intensity", param.get("intensity", 1),
                            "float", "Intensity of white value")
        self.info.add_param("img_size", param["img_size"], "pix",
                            "Width and height of each image")
        self.info.add_param("box_size", param["box_size"], "pix",
                            "Width and height of checkerboard box")
        self.info.add_param("length_unit", param["length_unit"],
                            "str", "Unit of length")
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Create checkerboard Image using Index table.

        Args:
            reqs[0] (pandas.DataFrame): Index table.
            param["img_size"] (list of int): Width and height of each image
                (pix).
            param["box_size"] (list of int):  The width and height of each
                checkerboard box in pixels.
            param["type"] (str): The value type of intensity.
            param["intensity" (int or str): The degree of whiteness in each
                frame. If "ascend" is specified, the degree of whiteness
                increases by one in each subsequent frame.

        Returns:
            Image: Checkerboard image stack.
        """
        df = reqs[0].copy()

        h_img, w_img = param["img_size"]
        h_box, w_box = param["box_size"]
        zero = np.zeros([h_box, w_box])
        one = np.ones([h_box, w_box])
        check = np.vstack([np.hstack([one, zero]), np.hstack([zero, one])])
        img = np.tile(check, (int(np.ceil(h_img / (h_box * 2))),
                              int(np.ceil(w_img / (w_box * 2)))))
        img = np.flipud(img[:h_img, :w_img]).astype(param["type"])

        stack = []
        for i in range(len(df)):
            if param["intensity"] == "ascend":
                stack.append(img * (i + 1))
            else:
                stack.append(img * param["intensity"])
        return np.array(stack)
