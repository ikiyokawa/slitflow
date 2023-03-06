import pytest

import slitflow as sf


@pytest.fixture
def Localization():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [3], "type": "image",
                "split_depth": 0})

    D2 = sf.loc.random.UniformRect()
    D2.run([D1], {"dimension": 2, "pitch": 0.1, "n_point": 10,
                  "lims": [[1, 9], [1, 9]], "length_unit": "um",
                  "split_depth": 0})
    return D2


def test_Gauss2D(Localization):
    D = sf.img.plot.Gauss2D()
    D.run([Localization],
          {"pitch": 0.1, "sd": 0.2, "img_size": [100, 100], "window_factor": 3,
          "group_depth": 1, "split_depth": 1})
    assert D.data[0].sum() > 0 and D.data[1].sum() > 0 and D.data[2].sum() > 0
