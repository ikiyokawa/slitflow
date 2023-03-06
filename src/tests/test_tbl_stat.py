import pytest
import numpy as np

import slitflow as sf


@pytest.fixture
def Index1():
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [1, 3], "type": "trajectory",
               "split_depth": 0})
    return D


def test_Mean(Index1):

    D = sf.tbl.stat.Mean()
    D.run([Index1], {"calc_col": "trj_no", "split_depth": 0})
    assert D.data[0]["trj_no"].values == np.array([2])

    del D
    Index1.set_split(1)
    D = sf.tbl.stat.Mean()
    D.run([Index1], {"calc_col": "trj_no", "split_depth": 0})
    assert D.data[0]["trj_no"].values == np.array([2]) and \
        D.data[0]["img_no"].values == np.array([1])


@pytest.fixture
def Index2():
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [3, 3, 3],
               "calc_cols": ["img_no", "trj_no", "value"],
               "split_depth": 0})
    return D


def test_Test(Index2):
    D = sf.tbl.stat.Test()
    D.run([Index2],
          {"sample_col": "img_no", "replicate_col": "trj_no",
           "calc_col": "value", "split_depth": 0})
    assert [len(D.data[0]), len(D.data[0].columns)] == [6, 21]
