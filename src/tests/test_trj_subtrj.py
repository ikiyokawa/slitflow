import pytest

import slitflow as sf


def test_Subtrajectory():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1, 3], "type": "trajectory",
                "split_depth": 0})

    D2 = sf.trj.random.WalkRect()
    D2.run([D1], {"diff_coeff": 0.1, "interval": 0.1, "n_step": 20,
                  "dimension": 2, "lims": [[1, 2], [1, 2]],
                  "length_unit": "um", "split_depth": 0})

    D3 = sf.trj.subtrj.Subtrajectory()
    D3.run([D2], {"step": 4, "group_depth": 2, "split_depth": 0})
    assert D3.data[0].shape == (255, 6)
