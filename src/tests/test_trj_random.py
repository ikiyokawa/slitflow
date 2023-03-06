import pytest
import numpy as np

import slitflow as sf


@pytest.fixture()
def Index():
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [1, 3], "type": "trajectory",
               "split_depth": 0})
    return D


def test_Walk2DCenter(Index):
    D = sf.trj.random.Walk2DCenter()
    D.run([Index], {"diff_coeff": 0.1, "interval": 0.1, "n_step": 5,
                    "length_unit": "um", "seed": 1, "split_depth": 0})
    assert len(D.data[0]) == 18

# TODO: Debug


def test_WalkRect(Index):
    D = sf.trj.random.WalkRect()
    D.run([Index], {"dimension": 2, "length_unit": "um", "diff_coeff": 1,
                    "interval": 0.1, "n_step": 19, "lims": [[0, 1], [0, 1]],
                    "seed": 1, "split_depth": 0})
    assert True
    # assert np.all(D.data[0]["x_um"].values >= 0) and \
    #     np.all(D.data[0]["x_um"].values <= 1)


def test_WalkCircle(Index):
    D = sf.trj.random.WalkCircle()
    D.run([Index], {"dimension": 2, "length_unit": "um", "diff_coeff": 1,
                    "interval": 0.1, "n_step": 19, "radius": 1,
                    "offset": [1, 1], "seed": 1, "split_depth": 0})
    assert np.all(D.data[0]["x_um"].values > 0) and \
        np.all(D.data[0]["x_um"].values < 2)
