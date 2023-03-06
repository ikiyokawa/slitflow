import pytest
import pandas as pd

import slitflow as sf


def test_Index():
    D1 = sf.tbl.create.Index()
    D1.run([],
           {"index_counts": [1, 1], "type": "trajectory", "split_depth": 0})
    assert D1.data[0].equals(pd.DataFrame({"img_no": [1], "trj_no": [1]}))

    D2 = sf.tbl.create.Index()
    D2.run([], {"index_counts": [1, 1], "type": "movie", "split_depth": 0})
    assert D2.data[0].equals(pd.DataFrame({"img_no": [1], "frm_no": [1]}))

    D3 = sf.tbl.create.Index()
    D3.run([], {"index_counts": [1, 1], "type": "movie", "index_value": 2,
                "split_depth": 0})
    assert D3.data[0].equals(pd.DataFrame({"img_no": [2], "frm_no": [1]}))

    D4 = sf.tbl.create.Index()
    D4.run([], {"index_counts": [1], "type": "image", "index_value": 2,
                "split_depth": 0})
    assert D4.data[0].equals(pd.DataFrame({"img_no": [2]}))

    D5 = sf.tbl.create.Index()
    D5.run([], {"index_counts": [1, 1, 1], "calc_cols":
                ["stack_no", "img_no", "point_no"], "split_depth": 0,
                "param": [["param_name", 1, "unit", "description"]]})
    assert D5.data[0].equals(
        pd.DataFrame({"stack_no": [1], "img_no": [1], "point_no": [1]}))
