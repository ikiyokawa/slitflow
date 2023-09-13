import numpy as np

from ..img.image import Image
from .. import RANDOM_SEED

np.random.seed(RANDOM_SEED)


class Gauss(Image):
    """Add Gaussian noise to all pixels.

    Args:
        reqs[0] (Image): Image to add noise. Required columns; ``intensity``.
        param["type"] (str, optional): The value type of intensity. Defaults to
            "float32".
        param["sigma"] (float, optional): The standard deviation of the
            Gaussian noise. Defaults to 1.
        param["baseline"] (float, optional): The baseline value of the
            background. Defaults to 0.
        param["seed"] (int, optional): The random seed.
        param["split_depth"] (int): The file split depth number.

    Returns:
        Image: The image with Gaussian noise.
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] then change and add columns.
        """
        self.info.copy_req(0)
        if "type" not in param:
            param["type"] = "float32"
        self.info.add_param("type", param["type"], "str",
                            "Value type of intensity")
        self.info.change_column_item("intensity", "type", param["type"])
        col_info = self.info.get_column_dict("intensity")
        self.info.add_param("sigma", param.get("sigma", 1), col_info["unit"],
                            "Standard deviation of Gaussian noise")
        self.info.add_param("baseline", param.get("baseline", 0),
                            col_info["unit"], "Baseline value of background")
        if "seed" in param:
            self.info.add_param("seed", param["seed"], "int", "Random seed")
            np.random.seed(param["seed"])
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Add Gaussian noise to all pixels.

        Args:
            reqs[0] (numpy.ndarray): The image to which noise is to be added.
            param["type"] (str): The value type of intensity.
            param["sigma"] (float): The standard deviation of the Gaussian
                noise.
            param["baseline"] (float): The baseline value of the background.

        Returns:
            numpy.ndarray: The image with Gaussian noise.
        """
        img = reqs[0].copy()
        noise = np.frompyfunc(gauss_noise, 3, 1)
        return noise(img, param["sigma"], param["baseline"]).\
            astype(param["type"])


def gauss_noise(x, sigma, baseline):
    """Adds Gaussian noise to an input pixel value.

    Args:
        x (float): Input pixel value.
        sigma (float): Standard deviation of the Gaussian noise.
        baseline (float): Baseline value of the noise.

    Returns:
        float: The input pixel value with added Gaussian noise.
    """
    return np.random.normal(loc=baseline, scale=sigma) + x
