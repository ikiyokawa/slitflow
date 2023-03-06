import pytest

import slitflow as sf


@pytest.fixture()
def Localization():
    D1 = sf.tbl.create.Index()
    D1.run([], {"type": "trajectory", "index_counts": [1, 3],
                "split_depth": 0})

    D2 = sf.trj.random.WalkRect()
    D2.run([D1], {"dimension": 2, "length_unit": "um", "diff_coeff": 0.1,
                  "interval": 0.1, "n_step": 4, "lims": [[1, 9], [1, 9]],
                  "split_depth": 0, "seed": 0})

    D3 = sf.tbl.convert.SortCols()
    D3.run([D2], {"new_depths": [1, 3, 2], "split_depth": 0})
    return D3


def test_LocalMax2Xy(Localization):
    D = sf.img.plot.Gauss2D()
    D.run([Localization], {"pitch": 0.1, "sd": 0.2, "img_size": [100, 100],
                           "window_factor": 3, "group_depth": 2,
                           "split_depth": 0})

    D1 = sf.img.filter.DifferenceOfGaussian()
    D1.run([D], {"wavelength": 0.6, "NA": 1.4, "split_depth": 0})

    D2 = sf.img.filter.LocalMax()
    D2.run([D1], {"split_depth": 2})

    D3 = sf.loc.convert.LocalMax2Xy()
    D3.run([D2], {"split_depth": 0})
    assert D3.data[0].shape == (13, 6)

    D2 = sf.img.filter.LocalMax()
    D2.run([D1], {"split_depth": 1})
    with pytest.raises(Exception) as e:
        D3 = sf.loc.convert.LocalMax2Xy()
        D3.run([D2], {"split_depth": 0})


def test_LocalMax2XyWithDoG(Localization):
    D = sf.img.plot.Gauss2D()
    D.run([Localization],
          {"pitch": 0.1, "sd": 0.2, "img_size": [100, 100],
           "window_factor": 3, "group_depth": 2, "split_depth": 2})

    D1 = sf.loc.convert.LocalMax2XyWithDoG()
    D1.run([D], {"wavelength": 0.6, "NA": 1.4, "split_depth": 0})
    to_avoid_float_variance = D1.data[0]["intensity"] > 0
    df = D1.data[0][to_avoid_float_variance]
    assert df.shape == (13, 6)

    del D
    D = sf.img.plot.Gauss2D()
    D.run([Localization],
          {"pitch": 0.1, "sd": 0.2, "img_size": [100, 100],
           "window_factor": 3, "group_depth": 2, "split_depth": 0})
    with pytest.raises(Exception) as e:
        D3 = sf.loc.convert.LocalMax2XyWithDoG()
        D3.run([D], {"wavelength": 0.6, "NA": 1.4, "split_depth": 0})
