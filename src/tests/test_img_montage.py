import pytest

import slitflow as sf


@pytest.fixture
def Images():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [4], "type": "image", "split_depth": 0})

    D2 = sf.img.create.Black()
    D2.run([D1], {"pitch": 0.1, "length_unit": "um",
                  "img_size": [100, 100], "split_depth": 0})

    D3 = sf.img.create.RandomRGB()
    D3.run([D1], {"pitch": 0.1, "length_unit": "um", "interval": 0.1,
                  "img_size": [100, 100], "split_depth": 0})
    return D2, D3


def test_Gray(Images):

    D = sf.img.montage.Gray()
    D.run([Images[0]], {"grid_shape": (2, 2), "padding_width": 1,
                        "split_depth": 0})
    assert D.data[0].shape == (1, 203, 203)


def test_RGB(Images):
    D = sf.img.montage.RGB()
    D.run([Images[1]], {"grid_shape": (2, 2), "padding_width": 1,
                        "split_depth": 0})
    assert D.data[0].shape == (3, 203, 203)
