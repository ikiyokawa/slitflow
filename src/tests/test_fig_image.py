import pytest
import numpy as np

import slitflow as sf


@pytest.fixture
def Gray():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1], "type": "image",
                "split_depth": 0})

    D2 = sf.img.create.Black()
    D2.run([D1], {"pitch": 0.1, "interval": 0.1,
                  "img_size": [5, 5], "length_unit": "um",
                  "split_depth": 1})
    D2.data[0][0, 2, :] = np.array([0, 1, 2, 3, 4])
    return D2


def test_Gray(Gray):
    D = sf.fig.image.Gray()
    D.run([Gray], {"lut_limits": [0, 4], "split_depth": 1})
    assert len(D.data[0].axes[0].get_children()) == 11
