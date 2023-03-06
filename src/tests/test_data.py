import pytest
import numpy as np
import pandas as pd

import slitflow as sf
from slitflow.name import make_info_path as ipath


def test_Data_pass():
    D = sf.data.Data()
    assert D.load_data("path") is None
    assert D.save_data("data", "path") is None
    assert D.split_data() is None
    assert D.set_info() is None
    assert D.post_run() is None
    assert D.process([1]) == 1


@pytest.fixture
def df_index():
    return pd.DataFrame({"img_no": [1], "trj_no": [1]})


def test_Data_run(df_index):
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})
    assert D.data[0].equals(df_index)

    D = sf.tbl.create.Index()
    D.run_mp([], {"index_counts": [1, 1], "type": "trajectory",
                  "split_depth": 0})
    assert D.data[0].equals(df_index)


def test_Data_memory_over():
    sf.data.Data.MEMORY_LIMIT = 0
    D = sf.tbl.create.Index()
    with pytest.raises(Exception) as e:
        D.run([], {"index_counts": [1, 1], "type": "trajectory",
                   "split_depth": 0})
    sf.data.Data.MEMORY_LIMIT = 0.9


def test_Data_io(tmpdir):
    D = sf.tbl.create.Index(ipath(tmpdir, 1, 1, "test", "ana", "grp"))
    D.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})
    D.save()

    D = sf.tbl.create.Index(ipath(tmpdir, 1, 1, "test", "ana", "grp"))
    D.load()

    sf.data.Data.MEMORY_LIMIT = 0
    D = sf.tbl.create.Index(ipath(tmpdir, 1, 1, "test", "ana", "grp"))
    with pytest.raises(Exception) as e:
        D.load()
    sf.data.Data.MEMORY_LIMIT = 0.9


def test_Data_split():
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})
    D.set_split(1)
    assert D.info.split_depth() == 1


def test_Data_set_reqs():
    D = sf.data.Data()
    D.set_reqs()
    assert np.isnan(D.reqs[0].data[0])
    del D

    D = sf.data.Data()
    D.set_reqs([1])
    assert D.reqs == [1]


@pytest.fixture
def df_info_index():
    return pd.DataFrame({"img_no": [1], "trj_no": [1], "_file": [0]})


def test_Data_set_index(df_info_index):
    R = sf.tbl.create.Index()
    R.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})

    D = sf.data.Data()
    D.set_reqs([R])
    D.info.copy_req(0)
    D.set_index()
    assert D.info.index.equals(df_info_index)


def test_Pickle_io(tmpdir):
    path = ipath(tmpdir, 1, 1, "test", "ana", "grp")
    D = sf.data.Pickle()
    D.save_data({"test": 1}, path)
    dic = D.load_data(path)
    assert dic["test"] == 1


def test_Pickle_split():
    D = sf.data.Pickle()
    D.data = [None]
    assert not D.split_data()
