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
