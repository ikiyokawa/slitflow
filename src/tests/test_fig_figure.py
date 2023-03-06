import os

import pytest

import slitflow as sf


@pytest.fixture
def Scatter():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1, 3], "type": "trajectory",
                "split_depth": 0})

    D2 = sf.trj.random.Walk2DCenter()
    D2.run([D1], {"diff_coeff": 0.1, "interval": 0.1, "n_step": 5,
                  "length_unit": "um", "split_depth": 0})
    D3 = sf.fig.scatter.Simple()
    D3.run([D2], {
        "calc_cols": ["x_um", "y_um"],
        "marker_styles": ["s", "o", "^"],
        "group_depth": 2, "split_depth": 0,
        "user_param": [
            ("size", [100, 100], "list", "Image size"),
            ("limit", [0, 1, 0, 1], "list", "Limit of axis")]})
    return D3


def test_Figure(tmpdir, Scatter):

    Scatter.save_data(Scatter.data[0], os.path.join(tmpdir, "test_fig.fig"))
    dct = Scatter.load_data(os.path.join(tmpdir, "test_fig.fig"))
    assert str(dct) == "Figure(640x480)"


def test_ToTiff(Scatter):
    D = sf.fig.figure.ToTiff()
    D.run([Scatter], {"scalebar": [1, 0.1, 0.1, 1, [0, 0, 0]],
                      "split_depth": 0})
    assert D.data[0].shape == (3, 1920, 2560)
