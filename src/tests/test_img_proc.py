import pytest

import slitflow as sf


def test_SelectParam():
    D1 = sf.tbl.create.Index()
    D1.run([], {"type": "movie", "index_counts": [2, 2],
                "split_depth": 1})

    D2 = sf.img.create.CheckerBoard()
    D2.run([D1], {"pitch": 0.1, "img_size": [100, 100], "box_size": [10, 10],
                  "intensity": "ascend", "length_unit": "um",
                  "split_depth": 1})

    D3 = sf.img.proc.SelectParam()
    D3.run([D2, D1], {"index": [(2, None)], "split_depth": 1})

    assert D3.data[0].shape == (2, 100, 100)


def test_SelectParam_Error():
    D1 = sf.tbl.create.Index()
    D1.run([], {"type": "movie", "index_counts": [2, 2],
                "split_depth": 0})

    D2 = sf.img.create.CheckerBoard()
    D2.run([D1], {"pitch": 0.1, "img_size": [100, 100], "box_size": [10, 10],
                  "intensity": "ascend", "length_unit": "um",
                  "split_depth": 1})

    D3 = sf.img.proc.SelectParam()
    with pytest.raises(Exception) as e:
        D3.run([D2, D1], {"index": [(2, None)], "split_depth": 1})
        assert e.match(
            "The split_depth of the input data is not equal to the ")
