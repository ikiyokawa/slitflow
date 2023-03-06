import pytest
import numpy as np
import tifffile as tf

import slitflow as sf


def test_SingleFile_SplitFile(tmpdir):

    path = tmpdir + "test_img.tif"
    stack = np.zeros((3, 100, 100))
    with tf.TiffWriter(path) as tif:
        for i in np.arange(0, stack.shape[0]):
            tif.write(np.flipud(stack[i, :, :]),
                      photometric="minisblack",
                      contiguous=True, description="",
                      resolution=(1, 1))

    D = sf.load.tif.SingleFile()
    D.run([], {"path": str(path), "length_unit": "um", "pitch": 0.1,
          "interval": 0.1, "value_type": "uint16", "split_depth": 0})
    assert D.data[0].shape == (3, 100, 100)

    del D
    D = sf.load.tif.SplitFile()
    D.run([], {"path": str(path), "length_unit": "um", "pitch": 0.1,
               "interval": 0.1, "value_type": "uint16",
               "indexes": [1], "split_depth": 0})
    assert D.data[0].shape == (3, 100, 100)
