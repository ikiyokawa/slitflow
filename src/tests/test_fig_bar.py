import pytest
import matplotlib.pyplot as plt

import slitflow as sf


@pytest.fixture
def Mean():
    D1 = sf.tbl.create.Index()
    D1.run([], {"type": "trajectory", "index_counts": [3, 4],
                "split_depth": 0})

    D2 = sf.tbl.stat.Mean()
    D2.run([D1], {"calc_col": "trj_no", "index_cols": ["img_no"],
                  "split_depth": 0})
    return D2


@pytest.fixture
def MeanSmall():
    D1 = sf.tbl.create.Index()
    D1.run([], {"type": "trajectory", "index_counts": [1, 2],
                "split_depth": 0})

    D2 = sf.tbl.stat.Mean()
    D2.run([D1], {"calc_col": "trj_no", "index_cols": ["img_no"],
                  "split_depth": 0})
    return D2


@pytest.fixture
def MeanDeep():
    D1 = sf.tbl.create.Index()
    D1.run([], {"calc_cols": ["img_no", "trj_no", "frm_no"],
                "index_counts": [3, 4, 5],
                "split_depth": 0})

    D2 = sf.tbl.stat.Mean()
    D2.run([D1], {"calc_col": "frm_no", "index_cols": ["img_no", "trj_no"],
                  "split_depth": 0})
    return D2


def test_Simple(Mean):
    D = sf.fig.bar.Simple()
    D.run([Mean], {"calc_cols": ["img_no", "trj_no"], "err_col": "std",
                   "group_depth": 1, "split_depth": 0})
    assert len(D.data[0].axes[0].get_children()) == 22
    del D

    D = sf.fig.bar.Simple()
    D.run([Mean], {"calc_cols": ["img_no", "trj_no"],
                   "group_depth": 1, "split_depth": 0})
    assert len(D.data[0].axes[0].get_children()) == 13
    del D

    D = sf.fig.bar.Simple()
    D.run([Mean], {"calc_cols": ["img_no", "trj_no"], "err_col": "std",
                   "group_depth": 0, "split_depth": 0})
    assert len(D.data[0].axes[0].get_children()) == 16
    del D

    D = sf.fig.bar.Simple()
    D.run([Mean], {"calc_cols": ["img_no", "trj_no"],
                   "group_depth": 0, "split_depth": 0})
    assert len(D.data[0].axes[0].get_children()) == 13
    del D


def test_WithModel(Mean, MeanDeep, MeanSmall):
    D = sf.fig.bar.WithModel()
    D.run([Mean, Mean], {"calc_cols": ["img_no", "trj_no"],
                         "group_depth": 1,
                         "model_cols": ["img_no", "trj_no"],
                         "group_depth_model": 1})
    assert len(D.data[0].axes[0].get_children()) == 16
    plt.close()
    del D

    D = sf.fig.bar.WithModel()
    D.run([Mean, Mean], {"calc_cols": ["img_no", "trj_no"], "err_col": "std",
                         "group_depth": 1,
                         "model_cols": ["img_no", "trj_no"],
                         "group_depth_model": 1})
    assert len(D.data[0].axes[0].get_children()) == 25
    plt.close()
    del D

    D = sf.fig.bar.WithModel()
    D.run([MeanDeep, MeanDeep], {"calc_cols": ["img_no", "frm_no"],
                                 "group_depth": 1,
                                 "model_cols": ["img_no", "frm_no"],
                                 "group_depth_model": 1})
    assert len(D.data[0].axes[0].get_children()) == 25
    plt.close()
    del D

    D = sf.fig.bar.WithModel()
    D.run([Mean, Mean], {"calc_cols": ["img_no", "trj_no"],
                         "group_depth": 0,
                         "model_cols": ["img_no", "trj_no"],
                         "group_depth_model": 0})
    assert len(D.data[0].axes[0].get_children()) == 14
    plt.close()
    del D

    D = sf.fig.bar.WithModel()
    D.run([Mean, Mean], {"calc_cols": ["img_no", "trj_no"], "err_col": "std",
                         "group_depth": 0,
                         "model_cols": ["img_no", "trj_no"],
                         "group_depth_model": 0})
    assert len(D.data[0].axes[0].get_children()) == 17
    plt.close()
    del D

    D = sf.fig.bar.WithModel()
    D.run([MeanSmall, MeanSmall], {"calc_cols": ["img_no", "trj_no"],
                                   "group_depth": 0,
                                   "model_cols": ["img_no", "trj_no"],
                                   "group_depth_model": 0})
    assert len(D.data[0].axes[0].get_children()) == 12
    plt.close()
