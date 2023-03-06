import pytest
import numpy as np

import slitflow as sf


@pytest.fixture
def Index():
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [1, 3], "type": "trajectory",
               "split_depth": 0})
    return D


def test_EvalOneCol(Index):

    D = sf.tbl.math.EvalOneCol()
    D.run([Index], {"calc_cols": ["trj_no"],
          "type": "log10", "split_depth": 0})
    assert np.all(D.data[0]["log10_trj_no"].values == np.log10([1, 2, 3]))

    del D
    D = sf.tbl.math.EvalOneCol()
    D.run([Index], {"calc_cols": ["trj_no"],
          "type": "one_", "eval": "x+1", "split_depth": 0})
    assert np.all(D.data[0]["one_trj_no"].values == np.array([2, 3, 4]))


def test_EvalTwoCols(Index):
    D = sf.tbl.math.EvalTwoCols()
    D.run([Index,
           Index],
          {"calc_cols": ["trj_no", "trj_no"], "eval": "x + y",
           "new_col_info": ("result", "int", "num", "Added trajectory number"),
           "split_depth": 0})
    assert np.all(D.data[0]["result"].values == np.array([2, 4, 6]))


def test_Centering(Index):
    D = sf.tbl.math.Centering()
    D.run([Index],
          {"calc_cols": ["trj_no"], "group_depth": 0, "split_depth": 0})
    assert np.all(D.data[0]["trj_no"].values == np.array([-1, 0, 1]))

    del D
    D = sf.tbl.math.Centering()
    D.run([Index],
          {"calc_cols": ["trj_no"], "group_depth": 1, "split_depth": 0})
    assert np.all(D.data[0]["trj_no"].values == np.array([-1, 0, 1]))


def test_AddGauss(Index):
    D = sf.tbl.math.AddGauss()
    D.run([Index],
          {"name": "rand", "unit": "none", "description": "random",
          "sigmas": [0.1, 0.2], "baselines": [10, 20], "ratio": [0.6, 0.4],
           "seed": 1, "split_depth": 0})
    assert np.all(
        np.round(D.data[0]["rand"].values) == np.array([10, 10, 20]))
