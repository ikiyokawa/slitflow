import os

import numpy as np
import pytest

import slitflow as sf
from slitflow.name import make_info_path as ipath


@pytest.fixture
def Index():
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [3], "type": "image", "split_depth": 0})
    return D


def test_Image(tmpdir, Index):
    path = os.path.join(tmpdir, "test.tif")
    D = sf.img.create.Black()
    D.run([Index], {"pitch": 0.1, "img_size": [10, 10], "length_unit": "um",
                    "split_depth": 0})
    D.save_data(D.data[0], path)
    D.load_data(path)
    assert D.data[0].shape == (3, 10, 10)

    D.split()
    assert D.data[0].shape == (3, 10, 10)

    D.data = []
    D.split()
    assert D.data == []

    D.save_data(np.array([]), path)
    D.data = [np.array([])]
    D.split()
    assert D.data[0].shape == (0,)


def test_Image_set_info(Index):
    D1 = sf.img.create.Black()
    D1.run([Index], {"pitch": 0.1, "img_size": [10, 10], "length_unit": "um",
                     "split_depth": 0})

    D2 = sf.img.image.Image()
    D2.set_reqs([D1])
    D2.set_info({"split_depth": 0})
    assert D2.info.get_param_names() ==\
        ['calc_cols', 'index_counts', 'pitch', 'type',
         'img_size', 'length_unit', 'split_depth']


def test_Image_memory_error(tmpdir, Index):
    path = os.path.join(tmpdir, "test.tif")

    D = sf.img.create.Black()
    D.run([Index], {"pitch": 0.1, "img_size": [10, 10], "length_unit": "um",
                    "split_depth": 0})
    D.save_data(D.data[0], path)

    D.memory_limit = 0
    with pytest.raises(Exception) as e:
        D.load_data(path)


def test_set_img_size(Index):
    D1 = sf.img.create.Black()
    D1.run([Index], {"pitch": 0.1, "img_size": [10, 10], "length_unit": "um",
                     "split_depth": 0})

    D2 = sf.img.montage.Gray()
    D2.run([D1], {"grid_shape": [2, 2], "padding_width": 1, "split_depth": 0})

    assert D2.info.get_param_value("img_size") == [23, 23]


def test_RGB(tmpdir, Index):
    path = os.path.join(tmpdir, "test.tif")
    D = sf.img.create.RandomRGB()
    D.run([Index], {"pitch": 0.1, "img_size": [10, 10], "length_unit": "um",
                    "split_depth": 0, "seed": 1})
    D.save_data(D.data[0], path)
    D.load_data(path)
    assert D.data[0].shape == (9, 10, 10)

    D.split()
    assert D.data[0].shape == (9, 10, 10)

    D.data = []
    D.split()
    assert D.data == []


def test_RGB_memory_error(tmpdir, Index):
    path = os.path.join(tmpdir, "test.tif")

    D = sf.img.create.RandomRGB()
    D.run([Index], {"pitch": 0.1, "img_size": [10, 10], "length_unit": "um",
                    "split_depth": 0})
    D.save_data(D.data[0], path)

    D.memory_limit = 0
    with pytest.raises(Exception) as e:
        D.load_data(path)


def test_RGB_to_imshow(Index):
    D = sf.img.create.RandomRGB()
    D.run([Index], {"pitch": 0.1, "img_size": [10, 10], "length_unit": "um",
                    "split_depth": 0})
    assert D.to_imshow(0).shape == (10, 10, 3)


def test_RGB_save_data(tmpdir, Index):
    path = os.path.join(tmpdir, "test.tif")
    D = sf.img.create.RandomRGB()
    D.run([Index], {"pitch": 0.1, "img_size": [10, 10], "length_unit": "um",
                    "split_depth": 0})
    D.info.delete_param("pitch")
    D.save_data(D.data[0], path)
    assert os.path.exists(path)
