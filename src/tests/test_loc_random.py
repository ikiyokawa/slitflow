import pytest
import numpy as np

import slitflow as sf


@pytest.fixture()
def Index():
    D = sf.tbl.create.Index()
    D.run([], {"type": "image", "index_counts": [1],
               "split_depth": 0})
    return D


def test_UniformRect(Index):
    D = sf.loc.random.UniformRect()
    D.run([Index], {"pitch": 0.1, "n_point": 3, "lims": [[0, 10], [0, 10]],
                    "length_unit": "um", "dimension": 2,
                    "seed": 1, "split_depth": 0})
    assert np.all(D.data[0]["x_um"].values >= 0) and \
        np.all(D.data[0]["x_um"].values <= 10)
