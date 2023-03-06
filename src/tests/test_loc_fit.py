import pytest

import slitflow as sf


@pytest.fixture()
def LocImg():
    D1 = sf.tbl.create.Index()
    D1.run([], {"type": "image", "index_counts": [3],
                "split_depth": 0})

    D2 = sf.loc.random.UniformRect()
    D2.run([D1], {"pitch": 0.1, "n_point": 3, "lims": [[1, 9], [1, 9]],
                  "length_unit": "um", "dimension": 2,
                  "seed": 1, "split_depth": 1})

    D3 = sf.img.plot.Gauss2D()
    D3.run([D2],
           {"pitch": 0.1, "sd": 0.2, "img_size": [100, 100],
           "window_factor": 5, "group_depth": 1, "split_depth": 1})

    D4 = sf.img.plot.Gauss2D()
    D4.run([D2],
           {"pitch": 0.1, "sd": 0.2, "img_size": [100, 100],
           "window_factor": 5, "group_depth": 1, "split_depth": 0})
    D2.data[0]["x_um"].values[0] = 0  # for out of image
    D2.data[0]["x_um"].values[1] = 9  # for fitting error
    return D2, D3, D4


def test_Gauss2D(LocImg):

    D = sf.loc.fit.Gauss2D()
    D.run([LocImg[1], LocImg[0]], {"half_width": 3, "split_depth": 0})
    assert D.data[0].shape == (9, 14)

    with pytest.raises(Exception) as e:
        D = sf.loc.fit.Gauss2D()
        D.run([LocImg[2], LocImg[0]], {"half_width": 3, "split_depth": 0})
