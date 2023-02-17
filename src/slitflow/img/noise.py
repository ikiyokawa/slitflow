import numpy as np

from ..img.image import Image
from .. import RANDOM_SEED

np.random.seed(RANDOM_SEED)


class Gauss(Image):
    """Add Gaussian noise to all pixels.

    Args:
        reqs[0] (Image): Image to add noise.
            Required columns; ``intensity``.
        param["sigma"] (float): Standard deviation of Gaussian noise.
        param["baseline"] (float): Baseline value of background.
        param["seed"] (int, optional): Random seed.
        param["split_depth"] (int): File split depth number.

    Returns:
        Image: Image with Gaussian noise
    """

    def set_info(self, param={}):
        """Copy info from reqs[0] then change and add columns.
        """
        self.info.copy_req(0)
        self.info.change_column_item("intensity", "type", "float32")
        col_info = self.info.get_column_dict("intensity")
        self.info.add_param("sigma", param["sigma"], col_info["unit"],
                            "Standard deviation of Gaussian noise")
        self.info.add_param("baseline", param["baseline"], col_info["unit"],
                            "Baseline value of background")
        if "seed" in param:
            self.info.add_param("seed", param["seed"], "int", "Random seed")
            np.random.seed(param["seed"])
        self.info.set_split_depth(param["split_depth"])

    @staticmethod
    def process(reqs, param):
        """Add Gaussian noise to all pixels.

        Args:
            reqs[0] (numpy.ndarray): Image to add noise.
            param["sigma"] (float): Standard deviation of Gaussian noise.
            param["baseline"] (float): Baseline value of background.

        Returns:
            numpy.ndarray: Image with Gaussian noise
        """
        img = reqs[0].copy()
        noise = np.frompyfunc(gauss_noise, 3, 1)
        return noise(img, param["sigma"], param["baseline"])


def gauss_noise(x, sigma, baseline):
    return np.random.normal(loc=baseline, scale=sigma) + x
