import pytest
import numpy as np

import slitflow as sf


def test_sort_nartural_sort():
    sorted = sf.fun.sort.natural_sort(["1", "10", "2", "3"])
    assert sorted == ["1", "2", "3", "10"]


def test_img():
    img = np.array([[1, 0], [0, 1]])
    img_lut = sf.fun.img.set_lut(img, -1, 3)
    assert np.allclose(img_lut, np.array([[0.5, 0.25], [0.25, 0.5]]))

    img_norm = sf.fun.img.norm_img_sd(img, 2, 2)
    assert np.allclose(img_norm, np.array([[0.75, 0.25], [0.25, 0.75]]))


def test_misc():
    assert sf.fun.misc.reduce_list(["a"]) == "a"
    assert sf.fun.misc.reduce_list(["a", "b"]) == ["a", "b"]


def test_palette():

    Lp = sf.fun.palette.Loop([1, 2])
    items = []
    for _, item in zip(range(3), Lp):
        items.append(item)
    assert items == [1, 2, 1]

    Lp = sf.fun.palette.NumberLoop([1, 2])
    items = []
    for _, item in zip(range(3), Lp):
        items.append(item)
    assert items == [1, 2, 1]

    Lp = sf.fun.palette.NumberLoop(1)
    items = []
    for _, item in zip(range(3), Lp):
        items.append(item)
    assert items == [1, 1, 1]

    Lp = sf.fun.palette.ColorLoop(None)
    items = []
    for _, item in zip(range(3), Lp):
        items.append(item)
    assert items == [None, None, None]

    Lp = sf.fun.palette.ColorLoop("umap_face")
    items = []
    for _, item in zip(range(3), Lp):
        items.append(item)
    assert items[1][0] == items[2][1]

    Lp = sf.fun.palette.ColorLoop("None")
    items = []
    for _, item in zip(range(3), Lp):
        items.append(item)
    assert items == ["None", "None", "None"]

    with pytest.raises(Exception) as e:
        Lp = sf.fun.palette.ColorLoop("NoneNone")

    Lp = sf.fun.palette.ColorLoop([0, 0, 0])
    items = []
    for _, item in zip(range(3), Lp):
        items.append(item)
    assert items[2] == (0.0, 0.0, 0.0)

    Lp = sf.fun.palette.ColorLoop([[0, 0, 0], None, "None"])
    items = []
    for _, item in zip(range(3), Lp):
        items.append(item)
    assert items == [(0.0, 0.0, 0.0), None, "None"]

    Lp = sf.fun.palette.LineStyleLoop(None)
    items = []
    for _, item in zip(range(3), Lp):
        items.append(item)
    assert items == [None, None, None]

    Lp = sf.fun.palette.LineStyleLoop("default")
    items = []
    for _, item in zip(range(3), Lp):
        items.append(item)
    assert items == ["solid", (0, (5, 1)), (0, (1, 1))]

    Lp = sf.fun.palette.LineStyleLoop("-")
    items = []
    for _, item in zip(range(3), Lp):
        items.append(item)
    assert items == ["-", "-", "-"]

    Lp = sf.fun.palette.LineStyleLoop(["-", ":"])
    items = []
    for _, item in zip(range(3), Lp):
        items.append(item)
    assert items == ["-", ":", "-"]

    Lp = sf.fun.palette.MarkerStyleLoop(None)
    items = []
    for _, item in zip(range(3), Lp):
        items.append(item)
    assert items == [None, None, None]

    Lp = sf.fun.palette.MarkerStyleLoop("default")
    items = []
    for _, item in zip(range(3), Lp):
        items.append(item)
    assert items == ["o", "s", "^"]

    Lp = sf.fun.palette.MarkerStyleLoop("o")
    items = []
    for _, item in zip(range(3), Lp):
        items.append(item)
    assert items == ["o", "o", "o"]

    Lp = sf.fun.palette.MarkerStyleLoop(["s", "x"])
    items = []
    for _, item in zip(range(3), Lp):
        items.append(item)
    assert items == ["s", "x", "s"]
