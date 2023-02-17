import numpy as np


def set_lut(img, low, high):
    """Normalize input image intensity to 0-1.
    
    Outer intensities are set to border values.

    Args:
        img (numpy.ndarray): Input 2D image.
        low (float): Lower bound of intensity.
        high (float): Upper bound of intensity.

    Returns:
        numpy.ndarray: Normalized input image
    """
    img = (img - low) / (high - low)
    img[img > 1] = 1
    img[img < 0] = 0
    return img


def norm_img_sd(img, low_sd, high_sd):
    """Normalize input image intensity using standard deviation factors.
    
    Outer intensities are set to border values.

    Args:
        img (numpy.ndarray): Input 2D image.
        low_sd (float): A factor to multiply the standard deviation of image
            intensity. Mean intensity - S.D * low_sd is used to lower bound. 
        high_sd (float): A factor to multiply the standard deviation of image
            intensity. Mean intensity + S.D * high_sd is used to upper bound. 

    Returns:
        numpy.ndarray: Normalized input image
    """

    ave = np.mean(img)
    sd = np.std(img)
    low_limit = ave - sd * low_sd
    high_limit = ave + sd * high_sd
    return set_lut(img, low_limit, high_limit)
