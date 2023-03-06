import pytest
import numpy as np

import slitflow as sf


def test_fit_1to0():
    D1 = sf.tbl.create.Index()
    D1.run([],
           {"index_counts": [1, 1], "type": "trajectory", "split_depth": 1})

    D2 = sf.tbl.create.Index()
    D2.run([],
           {"index_counts": [2, 1], "type": "trajectory", "split_depth": 1})

    reqs = sf.setreqs.fit_1to0([D1, D2])
    assert len(reqs[0].data) == 1 and len(reqs[1].data) == 1


def test_copy_1to0():
    D1 = sf.tbl.create.Index()
    D1.run([],
           {"index_counts": [2, 1], "type": "trajectory", "split_depth": 1})

    D2 = sf.tbl.create.Index()
    D2.run([],
           {"index_counts": [1, 1], "type": "trajectory", "split_depth": 1})

    reqs = sf.setreqs.copy_1to0([D1, D2])
    assert reqs[1].data[1] is None


def test_and_2reqs():
    D1 = sf.tbl.create.Index()
    D1.run([],
           {"index_counts": [1, 1], "type": "trajectory", "split_depth": 1})

    D2 = sf.tbl.create.Index()
    D2.run([],
           {"index_counts": [2, 1], "type": "trajectory", "split_depth": 1})

    reqs = sf.setreqs.and_2reqs([D1, D2])
    assert len(reqs[0].data) == 1 and len(reqs[1].data) == 1


def test_set_cols():
    D1 = sf.tbl.create.Index()
    D1.run([],
           {"index_counts": [1, 1], "type": "trajectory", "split_depth": 1})
    assert sf.setreqs.set_cols(D1.info.index) == ['img_no', 'trj_no']


def test_set_reqs_file_nos():
    assert sf.setreqs.set_reqs_file_nos([], 0) == ([], [])

    D1 = sf.tbl.create.Index()
    D1.run([],
           {"index_counts": [1, 1], "type": "trajectory", "split_depth": 1})
    D2 = sf.tbl.create.Index()
    D2.run([],
           {"index_counts": [2, 1], "type": "trajectory", "split_depth": 1})
    reqs_no, save_no = sf.setreqs.set_reqs_file_nos([D1, D2], 1)
    assert np.allclose(reqs_no, np.array([0., 0.])) and \
        np.allclose(save_no, np.array([0.]))

    reqs_no, save_no = sf.setreqs.set_reqs_file_nos([D1, D2], 0)
    assert np.allclose(reqs_no, np.array([0., 0.])) and \
        np.allclose(save_no, np.array([0.]))

    D1 = sf.tbl.create.Index()
    D1.run([],
           {"index_counts": [2, 1], "type": "trajectory", "split_depth": 1})
    D2 = sf.tbl.create.Index()
    D2.run([],
           {"index_counts": [2, 1], "type": "trajectory", "split_depth": 1})
    reqs_no, save_no = sf.setreqs.set_reqs_file_nos([D1, D2], 0)
    assert np.allclose(reqs_no, np.array([[0., 0.], [1., 1.]])) and \
        np.isnan(save_no[0])
