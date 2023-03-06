import pytest
import numpy as np

import slitflow as sf


def test_calc_MaskArea():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [2], "type": "image", "split_depth": 0})

    D2 = sf.img.create.Black()
    D2.run([D1], {"pitch": 0.1, "length_unit": "um", "interval": 0.1,
                  "img_size": [100, 100], "split_depth": 0})

    D2.data[0][1, 10:90, 10:90] = 1

    D3 = sf.img.calc.MaskArea()
    D3.run([D2], {"split_depth": 0})
    assert np.allclose(D3.data[0]["area"].values, np.array([0.0, 64.]))
