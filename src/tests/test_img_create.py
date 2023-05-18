import pytest

import slitflow as sf


@pytest.fixture
def Index():
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})
    return D


def test_Black(Index):
    D = sf.img.create.Black()
    D.run([Index], {"pitch": 0.1, "interval": 0.1,
                    "img_size": [100, 100], "length_unit": "um",
                    "split_depth": 0})
    assert D.data[0].shape == (1, 100, 100)


def test_RandomRGB(Index):
    D = sf.img.create.RandomRGB()
    D.run([Index], {"pitch": 0.1, "interval": 0.1, "img_size": [100, 100],
                    "seed": 1, "length_unit": "um",
                    "split_depth": 0})
    assert D.data[0].shape == (3, 100, 100)


def test_CheckerBoard(Index):
    D = sf.img.create.CheckerBoard()
    D.run([Index], {"pitch": 0.1, "img_size": [100, 100], "box_size": [10, 10],
                    "intensity": "ascend", "length_unit": "um",
                    "split_depth": 0})
    assert D.data[0].shape == (1, 100, 100)

    D = sf.img.create.CheckerBoard()
    D.run([Index], {"pitch": 0.1, "img_size": [100, 100], "box_size": [10, 10],
                    "intensity": 1, "length_unit": "um", "interval": 1,
                    "split_depth": 0})
    assert D.data[0].shape == (1, 100, 100)
