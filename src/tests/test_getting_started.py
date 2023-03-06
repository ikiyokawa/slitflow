import os

import pytest

import slitflow as sf


def test_basic(tmpdir):

    PL = sf.manager.Pipeline(tmpdir)
    obs_names = ["Sample1"]
    PL.add(sf.tbl.create.Index(), 0, (1, 1), "channel1", "index",
           obs_names, [], [],
           {"type": "trajectory", "index_counts": [2, 3], "split_depth": 0})
    PL.add(sf.trj.random.Walk2DCenter(), 0, (1, 2), None, "trj",
           obs_names, [(1, 1)], [0],
           {"diff_coeff": 0.1, "interval": 0.1, "n_step": 5,
            "length_unit": "um", "seed": 1, "split_depth": 0})
    PL.add(sf.trj.msd.Each(), 0, (1, 3), None, "msd",
           obs_names, [(1, 2)], [0],
           {"group_depth": 2, "split_depth": 0})
    PL.add(sf.tbl.stat.Mean(), 0, (1, 4), None, "avemsd",
           obs_names, [(1, 3)], [0],
           {"calc_col": "msd", "index_cols": ["interval"], "split_depth": 0})
    PL.add(sf.fig.line.Simple(), 0, (1, 5), None, "msd_fig",
           obs_names, [(1, 4)], [0],
           {"calc_cols": ["interval", "msd"], "err_col": "sem", "group_depth": 0, "split_depth": 0})
    PL.add(sf.fig.style.Basic(), 0, (1, 6), None, "msd_style",
           obs_names, [(1, 5)], [0],
           {"limit": [-0.01, 0.52, -0.005, 0.205], "tick": [[0, 0.1, 0.2, 0.3, 0.4, 0.5], [0, 0.05, 0.1, 0.15, 0.2]],
            "label": ["Interval (s)", "MSD (\u03bcm$^{2}$)"], "format": ["%.1f", "%.2f"]})
    PL.add(sf.fig.figure.ToTiff(), 0, (1, 7), None, "msd_img",
           obs_names, [(1, 6)], [0],
           {"split_depth": 0})
    PL.save("pipeline")
    PL.run()

    assert set(os.listdir(tmpdir)) == {"g0_config", "g1_channel1"}
