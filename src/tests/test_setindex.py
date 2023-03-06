import pytest
import pandas as pd

import slitflow as sf
from slitflow.name import make_info_path as ipath


def test_from_req():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [2], "type": "image", "split_depth": 0})

    D2 = sf.img.create.Black()
    D2.run([D1], {"pitch": 0.1, "length_unit": "um", "interval": 0.1,
                  "img_size": [100, 100], "split_depth": 0})

    D3 = sf.img.calc.MaskArea()
    D3.run([D2], {"split_depth": 0})
    assert D3.info.index.equals(
        pd.DataFrame({"img_no": [1, 2], "_file": [0, 0], "_split": [0, 0]}))


def test_from_req_pipeline(tmpdir):

    PL = sf.manager.Pipeline(tmpdir)
    obs_names = ['OBS_TEST1']

    PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj", "index",
           obs_names, [], [],
           {"calc_cols": ["dat_no", "img_no", "trj_no"],
            "index_counts": [3, 4, 10], "split_depth": 0})
    # add to existing index
    PL.add(sf.img.create.Black(), 2, (1, 2), None, 'img', obs_names,
           [(1, 1)], [1], {"pitch": 0.05, "img_size": [50, 50],
                           "split_depth": 1, "length_unit": "um"})
    PL.run()

    D = sf.img.image.Image(ipath(tmpdir, 1, 2, "OBS_TEST1"))
    assert D.info.index.shape == (120, 4)


def test_from_data():
    D = sf.tbl.create.Index()
    D.run([], {"index_counts": [1, 1], "type": "trajectory",
               "split_depth": 0})
    assert D.info.index.equals(
        pd.DataFrame({"img_no": [1], "trj_no": [1],
                      "_file": [0], "_split": [0]}))


# from_req_plus_data is tested in
# test_trj_wtrackpy.py test_Locate_RefineCoM_Link
