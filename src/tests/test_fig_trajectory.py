import pytest

import slitflow as sf


@pytest.fixture
def Walk2DCenter():
    R1 = sf.tbl.create.Index()
    R1.run([], {"index_counts": [1, 3], "type": "trajectory",
                "split_depth": 0})

    R2 = sf.trj.random.Walk2DCenter()
    R2.run([R1], {"diff_coeff": 0.1, "interval": 0.1, "n_step": 5,
                  "length_unit": "um", "split_depth": 0})
    return R2


def test_All(Walk2DCenter):

    D1 = sf.fig.trajectory.All()
    D1.run([Walk2DCenter], {"trj_depth": 2, "split_depth": 1})
    assert len(D1.data[0].axes[0].get_children()) == 13
    del D1

    D1 = sf.fig.trajectory.All()
    D1.run([Walk2DCenter],
           {"trj_depth": 2, "centered": True, "split_depth": 1})
    assert D1.data[0].axes[0].lines[0].get_xdata()[0] != 0

    D2 = sf.fig.trajectory.StyleAll()
    D2.run([D1], {"split_depth": 0})
    assert D2.data[0].axes[0].get_xlim() == (-10.0, 10.0)
    del D2

    D2 = sf.fig.trajectory.StyleAll()
    D2.run([D1], {"half_width": 5, "split_depth": 0})
    assert D2.data[0].axes[0].get_xlim() == (-5.0, 5.0)
    del D1, D2

    D1 = sf.fig.trajectory.All()
    D1.run([Walk2DCenter],
           {"trj_depth": 2, "split_depth": 1,
           "user_param": [
            ["img_size", [100, 100], "list of int", "Width and height"],
            ["pitch", 0.1, "um/pix", "Length per pixel"]]})

    D2 = sf.fig.trajectory.StyleAll()
    D2.run([D1], {"split_depth": 0})
    assert D2.data[0].axes[0].get_xlim() == (0.0, 10.0)
