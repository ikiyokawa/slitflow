import pytest
import pandas as pd

import slitflow as sf


@pytest.fixture
def Index():
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [1, 5], "type": "trajectory",
               "split_depth": 0})
    return D


def test_CutOffPixelQuantile(Index):

    D = sf.tbl.filter.CutOffPixelQuantile()
    D.run([Index], {"calc_col": "trj_no", "cut_factor": 0, "ignore_zero": True,
                    "split_depth": 0})

    assert D.data[0].equals(
        pd.DataFrame({"img_no": [1, 1], "trj_no": [4, 5]}))


def test_SelectParam(Index):
    D2 = sf.tbl.proc.SelectParam()
    D2.run([Index], {"index": [(1, [2, 3])], "split_depth": 1})

    assert D2.data[0].equals(
        pd.DataFrame({"img_no": [1, 1], "trj_no": [2, 3]}))


def test_SelectParam_pipeline(tmpdir):
    PL = sf.manager.Pipeline(tmpdir)
    PL.add(sf.tbl.create.Index(), 0, (2, 1), 'table', 'index',
           ["Sample1"], [], [],
           {"type": "movie", "index_counts": [3, 5], "split_depth": 1})
    PL.add(sf.tbl.proc.SelectParam(), 2, (2, 2), None, "sel",
           ["Sample1"], [(2, 1)], [1],
           {"index": [([2, 3], 3)], "split_depth": 1})
    PL.run()
