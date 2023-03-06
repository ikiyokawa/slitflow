import pytest
import numpy as np

import slitflow as sf


@pytest.fixture
def Black():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1, 1], "type": "trajectory",
                "split_depth": 0})
    D2 = sf.img.create.Black()
    D2.run([D1], {"pitch": 0.1, "interval": 0.1,
                  "img_size": [100, 100], "length_unit": "um",
                  "split_depth": 0})
    return D2


def test_Gauss(Black):
    D = sf.img.noise.Gauss()
    D.run([Black], {"sigma": 1, "baseline": 1, "seed": 1, "split_depth": 0})
    assert np.round(np.mean(D.data[0])) == 1
