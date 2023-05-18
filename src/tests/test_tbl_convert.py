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
    D.run([Index], {"new_depths": [0, 1], "split_depth": 0})
    assert D.data[0].equals(pd.DataFrame({"trj_no": [1], "img_no": [1]}))

    del D
    D = sf.tbl.convert.SortCols()
    with pytest.raises(Exception) as e:
        D.run([Index], {"new_depths": [0, 1, 1], "split_depth": 0})
    assert e.match("The number of new depths must be equal to the number\
                    of index columns in the table.")


def test_AddColumn():
    D1 = sf.tbl.create.Index()
    D1.run([], {"type": "image", "index_counts": [2],
                "split_depth": 0})

    D2 = sf.tbl.convert.AddColumn()
    D2.run([D1], {"col_info": [
        [3, "annot_no", "int32", "num", "Annotation number"],
        [0, "patch_class", "str", "str", "Patch class"],
        [0, "args", "str", "str", "Patch argument dictionary"]],
        "col_values": [
            [1, 1],
            ["FancyArrow", "Rectangle"],
            ['{"x": 1, "y": 1, "dx": -1, "dy": 1}',
             '{"xy": (2, 2), "width": 1, "height": 1}']],
        "split_depth": 1})
    assert D2.data[0].shape == (1, 4)

    del D2
    D2 = sf.tbl.convert.AddColumn()
    D2.run([D1], {"col_info":
                  [3, "annot_no", "int32", "num", "Annotation number"],
                  "col_values": [1, 1], "split_depth": 0})
    assert D2.data[0].shape == (2, 2)


def test_AddColumn_error():
    D1 = sf.tbl.create.Index()
    D1.run([], {"type": "image", "index_counts": [2],
                "split_depth": 1})

    D2 = sf.tbl.convert.AddColumn()
    with pytest.raises(Exception) as e:
        D2.run([D1], {"col_info": [
            [3, "annot_no", "int32", "num", "Annotation number"],
            [0, "patch_class", "str", "str", "Patch class"],
            [0, "args", "str", "str", "Patch argument dictionary"]],
            "col_values": [
                [1, 1],
                ["FancyArrow", "Rectangle"],
                ['{"x": 1, "y": 1, "dx": -1, "dy": 1}',
                 '{"xy": (2, 2), "width": 1, "height": 1}']],
            "split_depth": 2})
    assert e.match("Do not split the input table.")
