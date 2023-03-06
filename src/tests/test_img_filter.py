import pytest

import slitflow as sf


@pytest.fixture
def Black():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1, 1], "type": "trajectory",
                "split_depth": 0})
    D2 = sf.img.create.Black()
    D2.run([D1], {"pitch": 0.1, "interval": 0.1,
                  "img_size": [100, 100], "length_unit": "um",
                  "split_depth": 0})
    return D2


def test_Gauss(Black):
    D = sf.img.filter.Gauss()
    D.run([Black], {"kernel_size": 3, "split_depth": 0})
    assert D.data[0].shape == (1, 100, 100)


def test_DifferenceOfGaussian_LocalMax(Black):
    D1 = sf.img.filter.DifferenceOfGaussian()
    D1.run([Black], {"wavelength": 0.4, "NA": 1.4, "split_depth": 0})
    assert D1.data[0].shape == (1, 100, 100)

    D2 = sf.img.filter.LocalMax()
    D2.run([D1], {"split_depth": 0})
    assert D2.data[0].shape == (1, 100, 100)


def test_LocalMaxWithDoG(Black):
    D = sf.img.filter.LocalMaxWithDoG()
    D.run([Black], {"wavelength": 0.4, "NA": 1.4, "split_depth": 0})
    assert D.data[0].shape == (1, 100, 100)
