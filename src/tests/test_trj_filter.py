import pytest

import slitflow as sf


@pytest.fixture
def Walk2DCenter():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1, 3], "type": "trajectory",
                "split_depth": 0})

    D2 = sf.trj.random.Walk2DCenter()
    D2.run([D1], {"diff_coeff": 0.1, "interval": 0.1, "n_step": 5,
                  "length_unit": "um", "split_depth": 0})
    return D2


def test_StepAtLeast(Walk2DCenter):
    D1 = sf.trj.filter.StepAtLeast()
    D1.run([Walk2DCenter], {"step": 3, "group_depth": 2, "split_depth": 0})

    D2 = sf.trj.filter.StepAtLeast()
    D2.run([Walk2DCenter], {"step": 10, "group_depth": 2, "split_depth": 0})

    assert (len(D1.data[0]), len(D2.data[0])) == (18, 0)


def test_StepRange(Walk2DCenter):

    D1 = sf.trj.filter.StepRange()
    D1.run([Walk2DCenter], {"step_range": [5, 10],
                            "group_depth": 2, "split_depth": 0})

    D2 = sf.trj.filter.StepRange()
    D2.run([Walk2DCenter], {"step_range": [6, 10],
                            "group_depth": 2, "split_depth": 0})

    D3 = sf.trj.filter.StepRange()
    D3.run([Walk2DCenter], {"step_range": [3, 5],
                            "group_depth": 2, "split_depth": 0})

    assert (len(D1.data[0]), len(D2.data[0]), len(D3.data[0])) == (18, 0, 18)
