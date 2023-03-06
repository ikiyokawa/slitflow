import pytest

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


def test_Simple(Mean):
    D = sf.fig.line.Simple()
    D.run([Mean], {"calc_cols": ["img_no", "trj_no"], "err_col": "std",
                   "group_depth": 1, "split_depth": 0})
    assert len(D.data[0].axes[0].get_children()) == 22
    del D

    D = sf.fig.line.Simple()
    D.run([Mean], {"calc_cols": ["img_no", "trj_no"],
                   "group_depth": 1, "split_depth": 0})
    assert len(D.data[0].axes[0].get_children()) == 13
    del D

    D = sf.fig.line.Simple()
    D.run([Mean], {"calc_cols": ["img_no", "trj_no"], "err_col": "std",
                   "group_depth": 0, "split_depth": 0})
    assert len(D.data[0].axes[0].get_children()) == 14
    del D

    D = sf.fig.line.Simple()
    D.run([Mean], {"calc_cols": ["img_no", "trj_no"],
                   "group_depth": 0, "split_depth": 0})
    assert len(D.data[0].axes[0].get_children()) == 11


def test_WithModel(Mean):
    D = sf.fig.line.WithModel()
    D.run([Mean, Mean],
          {"calc_cols": ["img_no", "trj_no"], "err_col": "std",
           "model_cols": ["img_no", "trj_no"], "group_depth": 1,
           "group_depth_model": 1, "split_depth": 0})
    assert len(D.data[0].axes[0].get_children()) == 25
    del D

    D = sf.fig.line.WithModel()
    D.run([Mean, Mean],
          {"calc_cols": ["img_no", "trj_no"], "group_depth": 1,
           "model_cols": ["img_no", "trj_no"], "group_depth_model": 1,
           "split_depth": 0})
    assert len(D.data[0].axes[0].get_children()) == 16
    del D

    D = sf.fig.line.WithModel()
    D.run([Mean, Mean],
          {"calc_cols": ["img_no", "trj_no"], "err_col": "std",
           "model_cols": ["img_no", "trj_no"], "group_depth": 0,
           "group_depth_model": 0, "split_depth": 0})
    assert len(D.data[0].axes[0].get_children()) == 15
    del D

    D = sf.fig.line.WithModel()
    D.run([Mean, Mean],
          {"calc_cols": ["img_no", "trj_no"], "group_depth": 0,
           "model_cols": ["img_no", "trj_no"], "group_depth_model": 0,
           "split_depth": 0})
    assert len(D.data[0].axes[0].get_children()) == 12
