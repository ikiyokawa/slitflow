import pytest

import slitflow as sf


@pytest.fixture
def MixWalk2():

    n_trj = 1000
    n_step = 99
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1, n_trj], "type": "trajectory",
                "split_depth": 0})

    D2a = sf.trj.random.WalkRect()
    D2a.run([D1], {"dimension": 2, "length_unit": "um", "diff_coeff": 1,
                   "interval": 0.1, "n_step": n_step, "lims": [[1, 9], [1, 9]],
                   "seed": 0, "split_depth": 0})

    D2b = sf.trj.random.WalkRect()
    D2b.run([D1], {"dimension": 2, "length_unit": "um", "diff_coeff": 0.1,
                   "interval": 0.1, "n_step": n_step, "lims": [[1, 9], [1, 9]],
                   "seed": 1, "split_depth": 0})

    D3 = sf.tbl.convert.Obs2Depth()
    D3.run([D2a, D2b],
           {"col_name": "speed_no", "col_description": "Speed no",
            "obs_name": "new_name",
           "merged_obs_names": ["a", "b", "c"], "split_depth": 0})

    D4 = sf.tbl.convert.SortCols()
    D4.run([D3], {"new_depths": [2, 1, 3, 4], "split_depth": 0})
    return D4


@pytest.fixture
def MixWalk3():

    n_trj = 1000
    n_step = 99
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1, n_trj], "type": "trajectory",
                "split_depth": 0})

    D2a = sf.trj.random.WalkRect()
    D2a.run([D1], {"dimension": 2, "length_unit": "um", "diff_coeff": 1,
                   "interval": 0.1, "n_step": n_step, "lims": [[1, 9], [1, 9]],
                   "seed": 0, "split_depth": 0})

    D2b = sf.trj.random.WalkRect()
    D2b.run([D1], {"dimension": 2, "length_unit": "um", "diff_coeff": 0.1,
                   "interval": 0.1, "n_step": n_step, "lims": [[1, 9], [1, 9]],
                   "seed": 1, "split_depth": 0})

    D2c = sf.trj.random.WalkRect()
    D2c.run([D1], {"dimension": 2, "length_unit": "um", "diff_coeff": 0.01,
                   "interval": 0.1, "n_step": n_step, "lims": [[1, 9], [1, 9]],
                   "seed": 1, "split_depth": 0})

    D3 = sf.tbl.convert.Obs2Depth()
    D3.run([D2a, D2b, D2c],
           {"col_name": "speed_no", "col_description": "Speed no",
            "obs_name": "new_name",
           "merged_obs_names": ["a", "b", "c"], "split_depth": 0})

    D4 = sf.tbl.convert.SortCols()
    D4.run([D3], {"new_depths": [2, 1, 3, 4], "split_depth": 0})
    return D4


def test_JumpLenDist_PDF_2comp(MixWalk2):
    D1 = sf.trj.wfastspt.JumpLenDist()
    D1.run([MixWalk2], {"trj_depth": 2, "split_depth": 0})
    assert D1.data[0].shape == (1764, 4) and D1.data[0]["prob"].values[-1] == 0

    D2 = sf.trj.wfastspt.FitJumpLenDist2comp()
    D2.run([D1],
           {"lower_bound": [0.05, 0.0001, 0], "upper_bound": [25, 0.2, 1],
            "LocError": 0.035, "iterations": 1, "dZ": 0.700, "useZcorr": True,
            "a": 0.15716, "b": 0.20811, "split_depth": 0})

    D3 = sf.trj.wfastspt.ModelJumpLenDist()
    D3.run([D1, D2], {"show_pdf": True, "split_depth": 0})

    with pytest.raises(Exception) as e:
        D3 = sf.trj.wfastspt.ModelJumpLenDist()
        D3.run([D1, D2], {"show_pdf": False, "split_depth": 0})

    D2 = sf.trj.wfastspt.FitJumpLenDist2comp()
    D2.run([D1],
           {"lower_bound": [0.05, 0.0001, 0],
            "upper_bound": [25, 0.08, 1],
            "LocError": [0.01, 0.1],
            "iterations": 1, "dZ": 0.700, "useZcorr": False,
            "init": [0.5, 0.003, 0.3, 0.005], "split_depth": 0})

    D3 = sf.trj.wfastspt.ModelJumpLenDist()
    D3.run([D1, D2], {"show_pdf": True, "split_depth": 0})
    assert D3.data[0].shape == (882, 4)


def test_JumpLenDist_PDF_3comp(MixWalk3):
    D1 = sf.trj.wfastspt.JumpLenDist()
    D1.run([MixWalk3], {"trj_depth": 2, "split_depth": 0})
    assert D1.data[0].shape == (1764, 4) and D1.data[0]["prob"].values[-1] == 0

    D2 = sf.trj.wfastspt.FitJumpLenDist3comp()
    D2.run([D1],
           {"lower_bound": [0.1, 0.01, 0.001, 0, 0],
           "upper_bound": [2, 0.2, 0.02, 1, 1],
            "LocError": 0.035, "iterations": 1, "dZ": 0.700, "useZcorr": True,
            "a": 0.15716, "b": 0.20811, "split_depth": 0})

    D3 = sf.trj.wfastspt.ModelJumpLenDist()
    D3.run([D1, D2], {"show_pdf": True, "split_depth": 0})

    with pytest.raises(Exception) as e:
        D3 = sf.trj.wfastspt.ModelJumpLenDist()
        D3.run([D1, D2], {"show_pdf": False, "split_depth": 0})

    D2 = sf.trj.wfastspt.FitJumpLenDist3comp()
    D2.run([D1],
           {"lower_bound": [0.1, 0.01, 0.001, 0, 0],
           "upper_bound": [2, 0.2, 0.02, 1, 1],
            "LocError": [0.01, 0.1],
            "iterations": 1, "dZ": 0.700, "useZcorr": False,
            "init": [1, 0.1, 0.001, 0.33, 0.33, 0.05], "split_depth": 0})

    D3 = sf.trj.wfastspt.ModelJumpLenDist()
    D3.run([D1, D2], {"show_pdf": True, "split_depth": 0})
    assert D3.data[0].shape == (882, 4)


def test_JumpLenDist_CDF_2comp(MixWalk2):
    D1 = sf.trj.wfastspt.JumpLenDist()
    D1.run([MixWalk2], {"trj_depth": 2, "split_depth": 0, "CDF": True})
    assert D1.data[0].shape == (9639, 4)
    assert D1.data[0]["prob"].values[-1] > 0

    D2 = sf.trj.wfastspt.FitJumpLenDist2comp()
    D2.run([D1],
           {"lower_bound": [0.05, 0.0001, 0], "upper_bound": [25, 0.08, 1],
            "LocError": 0.035, "iterations": 1, "dZ": 0.700, "useZcorr": True,
            "a": 0.15716, "b": 0.20811, "split_depth": 0})

    D3 = sf.trj.wfastspt.ModelJumpLenDist()
    D3.run([D1, D2], {"show_pdf": True, "split_depth": 0})

    D2 = sf.trj.wfastspt.FitJumpLenDist2comp()
    D2.run([D1],
           {"lower_bound": [0.05, 0.0001, 0], "upper_bound": [25, 0.08, 1],
            "LocError": 0.035, "iterations": 1, "dZ": 0.700, "useZcorr": False,
            "init": [0.5, 0.003, 0.3], "split_depth": 0})

    D3 = sf.trj.wfastspt.ModelJumpLenDist()
    D3.run([D1, D2], {"show_pdf": False, "split_depth": 0})
    assert D3.data[0].shape == (8757, 4)


def test_JumpLenDist_CDF_3comp(MixWalk3):
    D1 = sf.trj.wfastspt.JumpLenDist()
    D1.run([MixWalk3], {"trj_depth": 2, "split_depth": 0, "CDF": True})
    assert D1.data[0].shape == (9639, 4)
    assert D1.data[0]["prob"].values[-1] > 0

    D2 = sf.trj.wfastspt.FitJumpLenDist3comp()
    D2.run([D1],
           {"lower_bound": [0.1, 0.01, 0.001, 0, 0],
           "upper_bound": [2, 0.2, 0.02, 1, 1],
            "LocError": 0.035, "iterations": 1, "dZ": 0.700, "useZcorr": True,
            "a": 0.15716, "b": 0.20811, "split_depth": 0})

    D3 = sf.trj.wfastspt.ModelJumpLenDist()
    D3.run([D1, D2], {"show_pdf": True, "split_depth": 0})

    D2 = sf.trj.wfastspt.FitJumpLenDist3comp()
    D2.run([D1],
           {"lower_bound": [0.1, 0.01, 0.001, 0, 0],
           "upper_bound": [2, 0.2, 0.02, 1, 1],
            "LocError": 0.035, "iterations": 1, "dZ": 0.700, "useZcorr": False,
            "init": [1, 0.1, 0.001, 0.33, 0.33], "split_depth": 0})

    D3 = sf.trj.wfastspt.ModelJumpLenDist()
    D3.run([D1, D2], {"show_pdf": False, "split_depth": 0})
    assert D3.data[0].shape == (8757, 4)
