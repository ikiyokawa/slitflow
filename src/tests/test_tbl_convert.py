import pytest
import pandas as pd

import slitflow as sf


@pytest.fixture
def Index():
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})
    return D


def test_SortCols(Index):
    D = sf.tbl.convert.SortCols()
    D.run([Index], {"new_depths": [2, 1], "split_depth": 0})
    assert D.data[0].equals(pd.DataFrame({"trj_no": [1], "img_no": [1]}))

    del D
    D = sf.tbl.convert.SortCols()
    D.run([Index], {"new_depths": [0], "split_depth": 0})
    assert D.data[0].equals(pd.DataFrame({"trj_no": [1], "img_no": [1]}))

# Obs2Depth is tested in the manager test
