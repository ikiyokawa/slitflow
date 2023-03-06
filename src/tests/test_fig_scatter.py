import pytest

import slitflow as sf


@pytest.fixture
def Randoms():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1, 3], "type": "trajectory",
                "split_depth": 0})

    D2 = sf.trj.random.Walk2DCenter()
    D2.run([D1], {"diff_coeff": 0.1, "interval": 0.1, "n_step": 5,
                  "length_unit": "um", "split_depth": 0})
    return D2


def test_Simple(Randoms):
    D = sf.fig.scatter.Simple()
    D.run([Randoms], {"calc_cols": ["x_um", "y_um"],
                      "marker_styles": ["s", "o", "^"],
                      "group_depth": 2, "split_depth": 0})
    assert len(D.data[0].axes[0].get_children()) == 13
    del D

    D = sf.fig.scatter.Simple()
    D.run([Randoms], {"calc_cols": ["x_um", "y_um"],
                      "marker_styles": "s",
                      "group_depth": 2, "split_depth": 0})
    assert len(D.data[0].axes[0].get_children()) == 13
    del D

    D = sf.fig.scatter.Simple()
    D.run([Randoms], {"calc_cols": ["x_um", "y_um"],
                      "marker_styles": "s",
                      "group_depth": 0, "split_depth": 0})
    assert len(D.data[0].axes[0].get_children()) == 11
