import pytest
import numpy as np
import pandas as pd

import slitflow as sf


@pytest.fixture
def Walk2DCenter():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1, 3], "type": "trajectory",
                "split_depth": 0})

    D2 = sf.trj.random.Walk2DCenter()
    D2.run([D1], {"diff_coeff": 0.1, "interval": 0.1, "n_step": 5,
                  "length_unit": "um", "split_depth": 0})
    return D2


@pytest.fixture
def EachMSD():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1, 3], "type": "trajectory",
                "split_depth": 0})

    D2 = sf.trj.random.Walk2DCenter()
    D2.run([D1], {"diff_coeff": 0.1, "interval": 0.1, "n_step": 5,
                  "length_unit": "um", "split_depth": 0})

    D3 = sf.trj.msd.Each()
    D3.run([D2], {"group_depth": 2, "split_depth": 0})

    return D3


@pytest.fixture
def MeanMSD():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1, 3], "type": "trajectory",
                "split_depth": 0})

    D2 = sf.trj.random.Walk2DCenter()
    D2.run([D1], {"diff_coeff": 0.1, "interval": 0.1, "n_step": 5,
                  "length_unit": "um", "split_depth": 0})

    D3 = sf.trj.msd.Each()
    D3.run([D2], {"group_depth": 2, "split_depth": 0})

    D4 = sf.tbl.stat.Mean()
    D4.run([D3], {"calc_col": "msd", "index_cols": ["interval"],
                  "split_depth": 0})
    return D4


def test_Each(Walk2DCenter):

    D = sf.trj.msd.Each()
    D.run([Walk2DCenter], {"group_depth": 2, "split_depth": 0})
    assert D.data[0].shape == (18, 4)


def test_FitAnom(MeanMSD, EachMSD):

    D1 = sf.trj.msd.FitAnom()
    D1.run([MeanMSD], {"step": 5, "group_depth": 2, "split_depth": 0})

    D2 = sf.trj.msd.ModelAnom()
    D2.run([D1], {"step": 0.01, "x_lims": [0, 1],
                  "group_depth": 2, "split_depth": 0})
    assert len(D1.data[0]), len(D2.data[0]) == (1, 100)

    del D1, D2
    D1 = sf.trj.msd.FitAnom()
    D1.run([EachMSD], {"step": 5, "group_depth": 2, "split_depth": 0})
    D2 = sf.trj.msd.ModelAnom()
    D2.run([D1], {"step": 0.01, "x_lims": [0, 1],
                  "group_depth": 3, "split_depth": 0})
    assert len(D1.data[0]), len(D2.data[0]) == (3, 300)


@pytest.fixture
def df_error():
    df = pd.DataFrame({"interval": [0, 1, 2, 3], "msd": np.full(4, np.inf)})
    param = {"step": 3}
    return df, param


def test_fit_msd_anom(df_error):
    result = sf.trj.msd.fit_msd_anom(*df_error)
    assert result.alpha == 0.5


def test_FitSimple(MeanMSD, EachMSD):
    D1 = sf.trj.msd.FitSimple()
    D1.run([MeanMSD], {"step": 5, "group_depth": 2, "split_depth": 0})

    D2 = sf.trj.msd.ModelSimple()
    D2.run([D1], {"step": 0.01, "x_lims": [0, 1],
                  "group_depth": 2, "split_depth": 0})
    assert len(D1.data[0]), len(D2.data[0]) == (1, 100)

    del D1, D2
    D1 = sf.trj.msd.FitSimple()
    D1.run([EachMSD], {"step": 5, "group_depth": 2, "split_depth": 0})

    D2 = sf.trj.msd.ModelSimple()
    D2.run([D1], {"step": 0.01, "x_lims": [0, 1],
                  "group_depth": 3, "split_depth": 0})
    assert len(D1.data[0]), len(D2.data[0]) == (3, 300)


def test_FitConfSaxton(MeanMSD, EachMSD):
    D1 = sf.trj.msd.FitConfSaxton()
    D1.run([MeanMSD], {"step": 5, "group_depth": 2, "split_depth": 0})

    D2 = sf.trj.msd.ModelConfSaxton()
    D2.run([D1], {"step": 0.01, "x_lims": [0, 1],
                  "group_depth": 2, "split_depth": 0})
    assert len(D1.data[0]), len(D2.data[0]) == (1, 100)

    del D1, D2
    D1 = sf.trj.msd.FitConfSaxton()
    D1.run([EachMSD], {"step": 5, "group_depth": 2, "split_depth": 0})

    D2 = sf.trj.msd.ModelConfSaxton()
    D2.run([D1], {"step": 0.01, "x_lims": [0, 1],
                  "group_depth": 3, "split_depth": 0})
    assert len(D1.data[0]), len(D2.data[0]) == (3, 300)


def test_fit_msd_confs(df_error):
    result = sf.trj.msd.fit_msd_confs(*df_error)
    assert result.equals(pd.Series({"diff_coeff": np.inf, "r": np.inf}))


def test_DfromDeltaV(Walk2DCenter):

    D = sf.trj.msd.DfromDeltaV()
    D.run([Walk2DCenter], {"group_depth": 2, "split_depth": 0})
    assert D.data[0].shape == (3, 3)
