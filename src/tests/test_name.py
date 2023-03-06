import os

import pytest

import slitflow as sf
from slitflow.name import make_info_path as ipath


def test_make_info_path(tmpdir):
    path = sf.name.make_info_path(tmpdir, 1, 1, "test", "ana", "grp")
    assert path == os.path.join(tmpdir, "g1_grp", "a1_ana", "test_grp_ana.sf")

    os.mkdir(path)
    path = sf.name.make_info_path(tmpdir, 1, 1, "test")
    assert path == os.path.join(tmpdir, "g1_grp", "a1_ana", "test_grp_ana.sf")

    os.mkdir(os.path.join(tmpdir, "g1_grp", "a1_ana2"))
    with pytest.raises(Exception) as e:
        path = sf.name.make_info_path(tmpdir, 1, 1, "test")

    with pytest.raises(Exception) as e:
        path = sf.name.make_info_path(tmpdir, 1, 2, "test")


def test_split_info_path(tmpdir):
    path = os.path.join(tmpdir, "g1_grp", "a1_ana", "test_grp_ana.sf")
    assert sf.name.split_info_path(path) == \
        (os.path.join(tmpdir, "g1_grp", "a1_ana"), "test", "ana", "grp")


def test_make_data_paths(tmpdir):
    D = sf.tbl.create.Index(ipath(tmpdir, 1, 1, "test", "ana", "grp"))
    D.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})
    D.save()
    assert sf.name.make_data_paths(D.info, ".csv") == \
        [os.path.join(tmpdir, "g1_grp", "a1_ana", "test_grp_ana.csv")]

    del D
    D = sf.tbl.create.Index(ipath(tmpdir, 1, 2, "test", "ana", "grp"))
    D.run([], {"index_counts": [2, 1], "type": "trajectory",
               "split_depth": 1})
    D.save()
    assert sf.name.make_data_paths(D.info, ".csv") == \
        [os.path.join(tmpdir, "g1_grp", "a2_ana", "test_D1_grp_ana.csv"),
         os.path.join(tmpdir, "g1_grp", "a2_ana", "test_D2_grp_ana.csv")]


def test_load_data_paths(tmpdir):
    D = sf.tbl.create.Index(ipath(tmpdir, 1, 1, "test", "ana", "grp"))
    D.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})
    D.save()
    assert sf.name.load_data_paths(D.info, ".csv") == \
        [os.path.join(tmpdir, "g1_grp", "a1_ana", "test_grp_ana.csv")]


def test_make_group(tmpdir):
    os.mkdir(os.path.join(tmpdir, "g1_grp2"))
    with pytest.raises(Exception) as e:
        sf.name.make_group(tmpdir, 1, "grp")


def test_get_obs_names(tmpdir):
    D = sf.tbl.create.Index(ipath(tmpdir, 1, 1, "test", "ana", "grp"))
    D.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})
    D.save()
    assert sf.name.get_obs_names(str(tmpdir), (1, 1)) == ["test"]

    os.mkdir(os.path.join(tmpdir, "g1_grp", "a1_ana2"))
    with pytest.raises(Exception) as e:
        sf.name.get_obs_names(str(tmpdir), (1, 1))

    assert sf.name.get_obs_names(str(tmpdir), (1, 3)) is None


def test_get_class_name(tmpdir):
    info_path = ipath(tmpdir, 1, 1, "test", "ana", "grp")
    D = sf.tbl.create.Index(info_path)
    D.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})
    D.save()
    assert sf.name.get_class_name(info_path) == \
        "sf.tbl.create.Index()"
