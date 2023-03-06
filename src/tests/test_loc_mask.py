import pytest

import slitflow as sf


@pytest.fixture()
def LocMask():
    D1 = sf.tbl.create.Index()
    D1.run([], {"type": "image", "index_counts": [2],
                "split_depth": 0})

    D2 = sf.loc.random.UniformRect()
    D2.run([D1], {"pitch": 0.1, "n_point": 100, "lims": [[0, 10], [0, 10]],
                  "length_unit": "um", "dimension": 2,
                  "seed": 1, "split_depth": 1})
    D2.data[0].iloc[0, 2] = -1  # for out of image handling

    D3 = sf.img.create.Black()
    D3.run([D1], {"pitch": 0.1, "img_size": [100, 100], "length_unit": "um",
                  "split_depth": 1})
    D3.data[0][:10, :] = 1

    D4 = sf.img.create.Black()
    D4.run([D1], {"pitch": 0.1, "img_size": [100, 100], "length_unit": "um",
                  "split_depth": 0})
    return D2, D3, D4


def test_Value(LocMask):

    D = sf.loc.mask.Value()
    D.run([LocMask[0], LocMask[1]], {"split_depth": 0})
    assert D.data[0].shape == (200, 3)

    del D
    D = sf.loc.mask.Value()
    D.run([LocMask[0], LocMask[1]], {"add_cols": ["x_um"], "split_depth": 0})
    assert D.data[0].shape == (200, 4)

    with pytest.raises(Exception) as e:
        D = sf.loc.mask.Value()
        D.run([LocMask[0], LocMask[2]], {"split_depth": 0})


def test_BinaryImage(LocMask):

    D = sf.loc.mask.BinaryImage()
    D.run([LocMask[0], LocMask[1]], {"split_depth": 0})
    assert D.data[0].shape == (99, 4)

    with pytest.raises(Exception) as e:
        D = sf.loc.mask.Value()
        D.run([LocMask[0], LocMask[2]], {"split_depth": 0})
