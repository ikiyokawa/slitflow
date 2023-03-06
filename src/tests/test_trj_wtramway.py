import pytest

import slitflow as sf


@pytest.fixture
def Walk2DCenter():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1, 10], "type": "trajectory",
                "split_depth": 0})

    D2 = sf.trj.random.Walk2DCenter()
    D2.run([D1], {"diff_coeff": 0.1, "interval": 0.1, "n_step": 19,
                  "length_unit": "um", "split_depth": 1})
    return D2


def test_TRamWAy(Walk2DCenter):

    D1 = sf.trj.wtramway.Tessellation()
    D1.run([Walk2DCenter], {"method": "gwr", "split_depth": 1})
    assert str(type(D1.data[0])) == \
        "<class 'tramway.tessellation.base.Partition'>"

    D2 = sf.trj.wtramway.Inference()
    D2.run([D1], {"mode": "d"})
    assert str(type(D2.data[0])) == \
        "<class 'tramway.inference.base.Maps'>"

    D3 = sf.trj.wtramway.MapPlot()
    D3.run([D1, D2], {"feature": "diffusivity"})
    assert str(type(D3.data[0])) == "<class 'matplotlib.figure.Figure'>"


def test_TRamWAy_with_param(Walk2DCenter):

    D1 = sf.trj.wtramway.Tessellation()
    D1.run([Walk2DCenter], {"method": "gwr",
           "split_depth": 1, "param": {"verbose": False}})
    assert str(type(D1.data[0])) == \
        "<class 'tramway.tessellation.base.Partition'>"

    D2 = sf.trj.wtramway.Inference()
    D2.run([D1], {"mode": "d", "param": {"inplace": False}})
    assert str(type(D2.data[0])) == \
        "<class 'tramway.inference.base.Maps'>"

    D3 = sf.trj.wtramway.MapPlot()
    D3.run([D1, D2], {"feature": "diffusivity", "param": {"unit": "std"}})

    assert str(type(D3.data[0])) == "<class 'matplotlib.figure.Figure'>"
