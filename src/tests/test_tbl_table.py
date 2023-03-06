import pytest
import pandas as pd

import slitflow as sf
from slitflow.name import make_info_path as ipath


def test_Table(tmpdir):

    path = ipath(tmpdir, 1, 1, "test", "ana", "grp")
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})
    D.save_data(D.data[0], path)
    D.load_data(path)
    assert D.data[0].equals(pd.DataFrame({"img_no": [1], "trj_no": [1]}))

    D.split_data()
    assert D.data[0].equals(pd.DataFrame({"img_no": [1], "trj_no": [1]}))

    D.data = []
    D.split_data()
    assert D.data == []

    del D
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})
    D.info.index = pd.DataFrame()
    D.split_data()
    assert D.data[0].equals(pd.DataFrame({"img_no": [1], "trj_no": [1]}))


# merge_different_index() is tested in loc.convert.LocalMax2Xy
