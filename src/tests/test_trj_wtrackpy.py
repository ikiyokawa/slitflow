import pytest

import slitflow as sf


@pytest.fixture()
def Gauss2D():
    D1 = sf.tbl.create.Index()
    D1.run([], {"type": "trajectory", "index_counts": [1, 3],
                "split_depth": 0})

    D2 = sf.trj.random.WalkRect()
    D2.run([D1], {"dimension": 2, "length_unit": "um", "diff_coeff": 0.1,
                  "interval": 0.1, "n_step": 4, "lims": [[1, 9], [1, 9]],
                  "seed": 0, "split_depth": 0})

    D3 = sf.tbl.convert.SortCols()
    D3.run([D2], {"new_depths": [1, 3, 2], "split_depth": 0})

    D4 = sf.img.plot.Gauss2D()
    D4.run([D3], {"pitch": 0.1, "sd": 0.2, "img_size": [100, 100],
                  "window_factor": 3, "group_depth": 2, "split_depth": 0})
    return D4


def test_Locate_RefineCoM_Link(Gauss2D):
    D1 = sf.trj.wtrackpy.Locate()
    D1.run([Gauss2D], {"diameter": 5, "split_depth": 0})

    assert D1.data[0].shape == (15, 11)

    D2 = sf.trj.wtrackpy.RefineCoM()
    D2.run([Gauss2D, D1], {"radius": 2, "split_depth": 0})
    assert D2.data[0].shape == (15, 6)

    D3 = sf.trj.wtrackpy.Link()
    D3.run([D2], {"search_range": 2, "split_depth": 0})
    assert D3.data[0].shape == (15, 5)
