import sys
import os

import pytest
import numpy as np

import slitflow as sf
from slitflow.name import make_info_path as ipath


def test_Info(tmpdir):
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})
    sys.stdout = open(os.path.join(tmpdir, "stdout_path_none.txt"), "w")
    print(D.info)
    sys.stdout.close()
    sys.stdout = sys.__stdout__
    print_text = open(os.path.join(tmpdir, "stdout_path_none.txt"), "r").read()
    assert "Data: slitflow.tbl.create.Index" in print_text \
        and "Path: None" in print_text

    D = sf.tbl.create.Index(ipath(tmpdir, 1, 1, "test", "ana", "grp"))
    D.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})
    sys.stdout = open(os.path.join(tmpdir, "stdout_with_path.txt"), "w")
    print(D.info)
    sys.stdout.close()
    sys.stdout = sys.__stdout__
    print_text = open(os.path.join(tmpdir, "stdout_with_path.txt"), "r").read()
    print(print_text)
    assert "Data: slitflow.tbl.create.Index" in print_text \
           and "Path: " + os.path.join(
               tmpdir, "g1_grp", "a1_ana", "test_grp_ana.sf") in print_text

    to_json = D.info.to_json()
    assert to_json.find('"meta": {') == 781

    D.info.meta = {}
    to_json = D.info.to_json()
    assert to_json.find('"meta": {') == 781


def test_Info_set_path(tmpdir):
    D = sf.tbl.create.Index(ipath(tmpdir, 1, 1, "test", "ana", "grp"))
    D.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})
    D.info.set_path("test_path")
    assert D.info.path == "test_path.sf"


def test_Info_load(tmpdir):
    D = sf.tbl.create.Index(ipath(tmpdir, 1, 1, "test", "ana", "grp"))
    D.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})
    D.save()
    del D

    D = sf.tbl.create.Index()
    D.info.load(ipath(tmpdir, 1, 1, "test", "ana", "grp"))
    assert D.info.meta["class"] == "slitflow.tbl.create.Index"


def test_Info_load_index(tmpdir):
    D1 = sf.tbl.create.Index(ipath(tmpdir, 1, 1, "test", "index", "grp"))
    D1.run([], {"index_counts": [1, 1], "type": "trajectory",
                "split_depth": 0})

    D2 = sf.tbl.stat.Mean(ipath(tmpdir, 1, 2, "test", "mean", "grp"))
    D2.run([D1], {"calc_col": "trj_no", "split_depth": 0})
    D2.save()

    del D2
    D2 = sf.tbl.stat.Mean(ipath(tmpdir, 1, 2, "test"))
    D2.load()
    assert len(D2.info.index) == 0


def test_Info_load_index_split(tmpdir):
    # This is how to save split data
    D1 = sf.tbl.create.Index(ipath(tmpdir, 1, 1, "test", "index", "grp"))
    D1.run([], {"index_counts": [2, 2], "type": "trajectory",
                "split_depth": 1})
    D1.save()

    del D1
    D1 = sf.tbl.create.Index(ipath(tmpdir, 1, 1, "test", "index", "grp"))
    D1.load(0)

    D2 = sf.trj.random.WalkRect(ipath(tmpdir, 1, 2, "test", "diff"))
    D2.run([D1], {"diff_coeff": 0.1, "interval": 0.1, "n_step": 2,
                  "dimension": 2, "lims": [[1, 2], [1, 2]],
                  "length_unit": "um", "split_depth": 1})
    D2.info.set_file_nos(0)
    D2.save()

    D1.load(1)
    del D2
    D2 = sf.trj.random.WalkRect(ipath(tmpdir, 1, 2, "test"))
    D2.run([D1], {"diff_coeff": 0.1, "interval": 0.1, "n_step": 2,
                  "dimension": 2, "lims": [[1, 2], [1, 2]],
                  "length_unit": "um", "split_depth": 1})
    D2.info.set_file_nos(1)
    D2.save()
    assert len(D2.info.index) == 12


def test_Info_set_file_nos():
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [2, 2], "type": "trajectory",
               "split_depth": 1})

    D.info.set_file_nos(np.nan)
    assert D.info.file_nos == [0, 1]

    D.info.set_file_nos([0, 1])
    assert D.info.file_nos == [0, 1]

    D.info.set_file_nos(np.array([0, 1]))
    assert D.info.file_nos == [0, 1]

    with pytest.raises(Exception) as e:
        D.info.set_file_nos("dummy")

    D.set_split(0)
    D2 = sf.tbl.stat.Mean()
    D2.run([D], {"calc_col": "trj_no", "split_depth": 0})
    D2.info.set_file_nos(np.nan)
    assert D2.info.file_nos == [0]


def test_Info_split():
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [2, 2], "type": "trajectory",
               "split_depth": 1})
    D.info.split()
    assert D.info.split_depth() == 1


def test_Info_column():
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [2, 2], "type": "trajectory",
               "split_depth": 1})
    D.info.add_column(2, "name", "type", "unit", "description")
    assert D.info.get_column_depth("name") == 2

    D.info.delete_column(keeps=["img_no", "trj_no"])
    assert D.info.get_column_name("all") == ["img_no", "trj_no"]
    assert D.info.get_column_name("col") == []

    D.info.change_column_item("img_no", "type", "float")
    assert D.info.get_column_type() == \
        {"img_no": "float", "trj_no": "int32"}

    with pytest.raises(Exception) as e:
        D.info.get_column_dict("frm_no")

    with pytest.raises(Exception) as e:
        D.info.column.append({"depth": 0,
                              "name": "img_no",
                              "type": "type",
                              "unit": "unit",
                              "description": "description"})
        D.info.get_column_dict("img_no")

    D.info.reset_depth("trj_no")
    assert D.info.get_column_depth("trj_no") == 4


def test_Info_param():
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [2, 2], "type": "trajectory",
               "split_depth": 1})
    D.info.add_param("_dummy", 0, "unit", "description")
    D.info.delete_private_param()
    assert D.info.get_param_names() == \
        ['calc_cols', 'index_counts', 'split_depth']

    D.info.set_group_depth(1)
    assert D.info.get_param_value("index_cols") == ["img_no"]

    D2 = sf.data.Data()
    D2.set_reqs([D])
    D2.info.copy_req(0, "index")
    D2.info.copy_req(0, "column")
    assert D2.info.get_column_name() == ["img_no", "trj_no"]

    D2.info.copy_req(0, "param")
    assert D2.info.get_param_names() == [
        'calc_cols', 'index_counts', 'split_depth',
        'group_depth', 'index_cols']

    del D
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [2, 2], "type": "trajectory",
               "split_depth": 1, "user_param": [("user", 1, "unit", "test")]})
    assert D.info.get_param_names() == [
        'calc_cols', 'index_counts', 'split_depth', 'user']


def test_fullname():
    D2 = sf.data.Data()
    assert sf.info.fullname(D2) == "slitflow.data.Data"
