import os

import pytest

import slitflow as sf


def test_Pipeline(tmpdir):
    root_dir = os.path.join(tmpdir, "prj")
    PL = sf.manager.Pipeline(root_dir)
    PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj", "index",
           ["Test"], None, None,
           {"index_counts": [1, 1], "type": "trajectory", "split_depth": 0})
    PL.save("pipeline")

    PL = sf.manager.Pipeline(root_dir)
    PL.run("pipeline")
    assert len(PL.df) == 1


def test_Pipeline_add_error(tmpdir):
    PL = sf.manager.Pipeline(tmpdir)
    with pytest.raises(Exception) as e:
        PL.add(None, 0, (1, 1), "trj", "index", [
               "Test"], None, None, {"split_depth": 0})
    with pytest.raises(Exception) as e:
        PL.add("dummy", 0, (1, 1), "trj", "index", ["Test"], None, None, {
               "index_counts": [1, 1], "type": "trajectory", "split_depth": 0})

    with pytest.raises(Exception) as e:
        PL.add(sf.tbl.create.Index(), 5, (1, 1), "trj", "index",
               ["Test"], None, None, {"split_depth": 0})

    with pytest.raises(Exception) as e:
        PL.add(sf.tbl.create.Index(), 0, [1, 1], "trj", "index",
               ["Test"], None, None, {"split_depth": 0})

    with pytest.raises(Exception) as e:
        PL.add(sf.tbl.create.Index(), 0, (1, 1, 1), "trj", "index",
               ["Test"], None, None, {"split_depth": 0})

    with pytest.raises(Exception) as e:
        PL.add(sf.tbl.create.Index(), 0, (1, 1), 1, "index",
               ["Test"], None, None, {"split_depth": 0})

    with pytest.raises(Exception) as e:
        PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj", 1,
               ["Test"], None, None, {"split_depth": 0})

    with pytest.raises(Exception) as e:
        PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj", "index",
               ["Test"], 1, None, {"split_depth": 0})

    with pytest.raises(Exception) as e:
        PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj", "index",
               ["Test"], [1], None, {"split_depth": 0})

    with pytest.raises(Exception) as e:
        PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj", "index",
               ["Test"], [(1, 1, 1)], None, {"split_depth": 0})

    with pytest.raises(Exception) as e:
        PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj", "index",
               [1], [], None, {"split_depth": 0})

    with pytest.raises(Exception) as e:
        PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj", "index",
               ["Test"], [], {1}, {"split_depth": 0})

    with pytest.raises(Exception) as e:
        PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj", "index",
               ["Test"], [(1, 1)], [], {"split_depth": 0})

    with pytest.raises(Exception) as e:
        PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj", "index",
               ["Test"], [], [], 1)


def test_Pipeline_add(tmpdir):
    PL = sf.manager.Pipeline(tmpdir)
    PL.add(sf.tbl.create.Index(), "0", None, None, "index",
           None, None, None, None)


def test_Pipeline_convert_indices(tmpdir):

    rootdir = os.path.join(tmpdir, 'B')
    PL = sf.manager.Pipeline(rootdir)
    for i in range(5):
        PL.add(sf.tbl.create.Index(), 0, (i + 1, 1), "trj", "index",
               ["test"], None, None, {"index_counts": [1, 1],
               "type": "trajectory", "split_depth": 0})
    PL.run(indices=1)
    assert set(os.listdir(rootdir)) == {'g0_config', 'g2_trj'}

    del PL
    rootdir = os.path.join(tmpdir, 'C')
    PL = sf.manager.Pipeline(rootdir)
    for i in range(5):
        PL.add(sf.tbl.create.Index(), 0, (i + 1, 1), "trj", "index",
               ["test"], None, None, {"index_counts": [1, 1],
               "type": "trajectory", "split_depth": 0})
    PL.run(indices=-1)
    assert set(os.listdir(rootdir)) == {'g0_config', 'g5_trj'}

    del PL
    rootdir = os.path.join(tmpdir, 'D')
    PL = sf.manager.Pipeline(rootdir)
    for i in range(5):
        PL.add(sf.tbl.create.Index(), 0, (i + 1, 1), "trj", "index",
               ["test"], None, None, {"index_counts": [1, 1],
               "type": "trajectory", "split_depth": 0})
    PL.run(indices=(3, None))
    assert set(os.listdir(rootdir)) == {"g0_config", "g4_trj", "g5_trj"}

    del PL
    rootdir = os.path.join(tmpdir, 'E')
    PL = sf.manager.Pipeline(rootdir)
    for i in range(5):
        PL.add(sf.tbl.create.Index(), 0, (i + 1, 1), "trj", "index",
               ["test"], None, None, {"index_counts": [1, 1],
               "type": "trajectory", "split_depth": 0})
    PL.run(indices=(2, 4))
    assert set(os.listdir(rootdir)) == {"g0_config", "g3_trj", "g4_trj"}

    del PL
    rootdir = os.path.join(tmpdir, 'F')
    PL = sf.manager.Pipeline(rootdir)
    for i in range(5):
        PL.add(sf.tbl.create.Index(), 0, (i + 1, 1), "trj", "index",
               ["test"], None, None, {"index_counts": [1, 1],
               "type": "trajectory", "split_depth": 0})
    PL.run(indices=(0, None, 2))
    assert set(os.listdir(rootdir)) == \
        {"g0_config", "g1_trj", "g3_trj", "g5_trj"}

    del PL
    rootdir = os.path.join(tmpdir, 'G')
    PL = sf.manager.Pipeline(rootdir)
    for i in range(5):
        PL.add(sf.tbl.create.Index(), 0, (i + 1, 1), "trj", "index",
               ["test"], None, None, {"index_counts": [1, 1],
               "type": "trajectory", "split_depth": 0})
    PL.run(indices=(0, 4, 2))
    assert set(os.listdir(rootdir)) == \
        {"g0_config", "g1_trj", "g3_trj"}

    del PL
    rootdir = os.path.join(tmpdir, 'H')
    PL = sf.manager.Pipeline(rootdir)
    for i in range(5):
        PL.add(sf.tbl.create.Index(), 0, (i + 1, 1), "trj", "index",
               ["test"], None, None, {"index_counts": [1, 1],
               "type": "trajectory", "split_depth": 0})
    PL.run(indices=range(3))
    assert set(os.listdir(rootdir)) == \
        {"g0_config", "g1_trj", "g2_trj", "g3_trj"}


def test_Pipeline_run(tmpdir):
    PL = sf.manager.Pipeline(tmpdir)
    PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj1", "index",
           ["Test"], None, None,
           {"index_counts": [1, 1], "type": "trajectory", "split_depth": 1})
    PL.add(sf.trj.random.WalkRect(), 0, (2, 1), "trj2", "random",
           None, [(1, 1)], [2],
           {"diff_coeff": 0.1, "interval": 0.1, "n_step": 2,
            "dimension": 2, "lims": [[1, 2], [1, 2]],
            "length_unit": "um", "split_depth": 0})
    PL.add(sf.trj.random.WalkRect(), 1, (3, 1), "trj3", "random",
           ["Test"], [(1, 1)], [2],
           {"diff_coeff": 0.1, "interval": 0.1, "n_step": 2,
            "dimension": 2, "lims": [[1, 2], [1, 2]],
            "length_unit": "um", "split_depth": 0})
    PL.add(sf.trj.random.WalkRect(), 2, (4, 1), "trj4", "random",
           ["Test"], [(1, 1)], [2],
           {"diff_coeff": 0.1, "interval": 0.1, "n_step": 2,
            "dimension": 2, "lims": [[1, 2], [1, 2]],
            "length_unit": "um", "split_depth": 0})
    PL.add(sf.trj.random.WalkRect(), 3, (5, 1), "trj5", "random",
           ["Test"], [(1, 1)], [2],
           {"diff_coeff": 0.1, "interval": 0.1, "n_step": 2,
            "dimension": 2, "lims": [[1, 2], [1, 2]],
            "length_unit": "um"})
    PL.run()
    assert set(os.listdir(tmpdir)) == \
        {"g0_config", "g1_trj1", "g2_trj2", "g3_trj3", "g4_trj4", "g5_trj5"}

    PL = sf.manager.Pipeline(tmpdir)
    PL.add(sf.tbl.create.Index(), 3, (1, 2), None, "index2",
           ["Test"], None, None,
           {"index_counts": [1, 1], "type": "trajectory", "split_depth": 1})
    with pytest.raises(Exception) as e:
        PL.run()


def test_Obs2Depth_table(tmpdir):
    PL = sf.manager.Pipeline(tmpdir)
    PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj", "index",
           ["Test1", "Test2"], None, None,
           {"index_counts": [1, 1], "type": "trajectory", "split_depth": 0})
    PL.add(sf.tbl.convert.Obs2Depth(), 0, (2, 1), "mrg", "mrg",
           ["Test1", "Test2"], [(1, 1), (1, 1)], [0, 0],
           {"obs_name": "Test", "split_depth": 0})
    PL.run()
    assert set(os.listdir(tmpdir)) == {"g0_config", "g1_trj", "g2_mrg"}


def test_Obs2Depth_image(tmpdir):
    PL = sf.manager.Pipeline(tmpdir)
    PL.add(sf.tbl.create.Index(), 0, (1, 1), "img", "index",
           ["Test1", "Test2"], None, None,
           {"index_counts": [1], "type": "image", "split_depth": 0})
    PL.add(sf.img.create.Black(), 0, (1, 2), None, "black",
           ["Test1", "Test2"], [(1, 1)], [0],
           {"pitch": 0.1, "img_size": [10, 10], "length_unit": "um",
           "split_depth": 0})
    PL.add(sf.img.convert.Obs2Depth(), 0, (2, 1), "mrg", "mrg",
           ["Test1", "Test2"], [(1, 2), (1, 2)], [0, 0],
           {"obs_name": "Test", "split_depth": 0})
    PL.run()
    assert set(os.listdir(tmpdir)) == {"g0_config", "g1_img", "g2_mrg"}


def test_Obs2Depth_image_no_index(tmpdir):
    PL = sf.manager.Pipeline(tmpdir)
    PL.add(sf.tbl.create.Index(), 0, (1, 1), "img", "index",
           ["Test1", "Test2"], None, None,
           {"index_counts": [1], "type": "image", "split_depth": 0})
    PL.add(sf.tbl.convert.SortCols(), 0, (1, 2), "img", "no_index",
           ["Test1", "Test2"], [(1, 1)], [0],
           {"new_depths": [0], "split_depth": 0})
    PL.add(sf.img.create.Black(), 0, (1, 3), None, "black",
           ["Test1", "Test2"], [(1, 2)], [0],
           {"pitch": 0.1, "img_size": [10, 10], "length_unit": "um",
           "split_depth": 0})
    PL.add(sf.img.convert.Obs2Depth(), 0, (2, 1), "mrg", "mrg",
           ["Test1", "Test2"], [(1, 3), (1, 3)], [0, 0],
           {"obs_name": "Test", "split_depth": 0})
    PL.run()
    assert set(os.listdir(tmpdir)) == {"g0_config", "g1_img", "g2_mrg"}


def test_Obs2Depth_RGB(tmpdir):
    PL = sf.manager.Pipeline(tmpdir)
    PL.add(sf.tbl.create.Index(), 0, (1, 1), "img", "index",
           ["Test1", "Test2"], None, None,
           {"index_counts": [1], "type": "image", "split_depth": 0})
    PL.add(sf.img.create.RandomRGB(), 0, (1, 2), None, "black",
           ["Test1", "Test2"], [(1, 1)], [0],
           {"pitch": 0.1, "img_size": [10, 10], "length_unit": "um",
           "split_depth": 0})
    PL.add(sf.img.convert.Obs2DepthRGB(), 0, (2, 1), "mrg", "mrg",
           ["Test1", "Test2"], [(1, 2), (1, 2)], [0, 0],
           {"obs_name": "Test", "split_depth": 0})
    PL.run()
    assert set(os.listdir(tmpdir)) == {"g0_config", "g1_img", "g2_mrg"}


def test_Pipeline_Delete(tmpdir):
    PL = sf.manager.Pipeline(tmpdir)
    PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj", "index",
           ["Test1", "Test2", "Test3"], None, None,
           {"index_counts": [1, 1], "type": "trajectory", "split_depth": 0})
    PL.add("Delete()", 0, None, None, "index",
           ["Test1"], [(1, 1)], [0], {})
    PL.add("Delete()", 0, None, None, "index",
           ["Test2"], [(1, 1)], [0], {"keep": "info"})
    PL.add("Delete()", 0, None, None, "index",
           ["Test3"], [(1, 1)], [0], {"keep": "folder"})
    PL.run()
    assert set(os.listdir(os.path.join(tmpdir, "g1_trj", "a1_index"))) ==\
        {'Test2_trj_index.sf'}

    PL.add(sf.tbl.create.Index(), 0, (1, 2), "trj", "index",
           ["Test1"], None, None,
           {"index_counts": [1, 1], "type": "trajectory", "split_depth": 0})
    PL.add("Delete()", 0, None, None, "index",
           ["Test1"], [(1, 2)], [0], {})
    assert not os.path.exists(os.path.join(tmpdir, "g1_trj", "a2_index"))


def test_Pipeline_Copy(tmpdir):

    PL = sf.manager.Pipeline(tmpdir)
    PL.add(sf.tbl.create.Index(), 0, (1, 1), "one", "index", ["Obs1"], [], [],
           {"type": "image", "index_counts": [3], "split_depth": 0})
    PL.add("Copy", 0, (1, 2), "one", "copy", ["Obs1Copy"], [(1, 1)], [0],
           {"obs_name": "Obs1"})
    PL.run()
    assert set(os.listdir(os.path.join(tmpdir, "g1_one", "a2_copy"))) ==\
        {'Obs1Copy_one_copy.csv', 'Obs1Copy_one_copy.sf',
         'Obs1Copy_one_copy.sfx'}

    del PL
    PL = sf.manager.Pipeline(tmpdir)
    PL.add(sf.tbl.create.Index(), 0, (1, 1), "one", "index", ["Obs1"], [], [],
           {"type": "image", "index_counts": [3], "split_depth": 0})
    PL.add("Copy", 0, (1, 2), "one", "copy", ["Obs1Copy"],
           [(1, 1), (1, 1)], [0, 0], {"obs_name": "Obs1"})
    with pytest.raises(Exception) as e:
        PL.run()

    del PL
    PL = sf.manager.Pipeline(tmpdir)
    PL.add(sf.tbl.create.Index(), 0, (1, 1), "one", "index", ["Obs1"], [], [],
           {"type": "image", "index_counts": [3], "split_depth": 0})
    PL.add("Copy", 0, (1, 2), "one", "copy", ["Obs1Copy", "Obs2Copy"],
           [(1, 1)], [0], {"obs_name": "Obs1"})
    with pytest.raises(Exception) as e:
        PL.run()

    del PL
    PL = sf.manager.Pipeline(tmpdir)
    PL.add(sf.tbl.create.Index(), 0, (1, 1), "one", "index", ["Obs1"], [], [],
           {"type": "image", "index_counts": [3], "split_depth": 0})
    PL.add("Copy", 0, (2, 1), None, "copy", ["Obs1Copy"], [(1, 1)], [0],
           {"obs_name": "Obs1"})
    with pytest.raises(Exception) as e:
        PL.run()


def test_Pipeline_make_flowchart(tmpdir):
    PL = sf.manager.Pipeline(tmpdir)
    PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj1", "index",
           ["Test"], None, None,
           {"index_counts": [1, 1], "type": "trajectory", "split_depth": 0})
    PL.add(sf.trj.random.WalkRect(), 0, (2, 1), "trj2", "random",
           None, [(1, 1)], [2],
           {"diff_coeff": 0.1, "interval": 0.1, "n_step": 2,
            "dimension": 2, "lims": [[1, 2], [1, 2]],
            "length_unit": "um", "split_depth": 0})
    PL.make_flowchart("test", "grp_ana")
    assert os.path.exists(os.path.join(tmpdir, "g0_config", "test.png"))

    del PL
    PL = sf.manager.Pipeline(tmpdir)
    PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj1", "index",
           ["Test"], None, None,
           {"index_counts": [1, 1], "type": "trajectory", "split_depth": 0})
    PL.add(sf.trj.random.WalkRect(), 0, (2, 1), "trj2", "random",
           None, [(1, 1)], [2],
           {"diff_coeff": 0.1, "interval": 0.1, "n_step": 2,
            "dimension": 2, "lims": [[1, 2], [1, 2]],
            "length_unit": "um", "split_depth": 0})
    PL.make_flowchart("test", "class_desc", is_vertical=True)
    assert os.path.exists(os.path.join(tmpdir, "g0_config", "test.png"))

    del PL
    PL = sf.manager.Pipeline(tmpdir)
    PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj1", "index",
           ["Test"], None, None,
           {"index_counts": [1, 1], "type": "trajectory", "split_depth": 0})
    PL.add(sf.trj.random.WalkRect(), 0, (2, 1), "trj2", "random",
           None, [(1, 1)], [2],
           {"diff_coeff": 0.1, "interval": 0.1, "n_step": 2,
            "dimension": 2, "lims": [[1, 2], [1, 2]],
            "length_unit": "um", "split_depth": 0})
    with pytest.raises(Exception) as e:
        PL.make_flowchart("test", "grp_name", is_vertical=True)
