import os

import pytest
import numpy as np
import matplotlib as mpl

import slitflow as sf


@pytest.fixture
def Lines():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1, 3], "type": "trajectory",
                "split_depth": 0})

    D2 = sf.trj.random.Walk2DCenter()
    D2.run([D1], {"diff_coeff": 0.1, "interval": 0.1, "n_step": 5,
                  "length_unit": "um", "split_depth": 0})

    D3 = sf.fig.line.Simple()
    D3.run([D2], {"calc_cols": ["x_um", "y_um"],
                  "group_depth": 2, "split_depth": 0})
    return D3


@pytest.fixture
def Scatters():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1, 3], "type": "trajectory",
                "split_depth": 0})

    D2 = sf.trj.random.Walk2DCenter()
    D2.run([D1], {"diff_coeff": 0.1, "interval": 0.1, "n_step": 5,
                  "length_unit": "um", "split_depth": 0})

    D3 = sf.fig.scatter.Simple()
    D3.run([D2], {"calc_cols": ["x_um", "y_um"],
                  "marker_styles": ["s", "o", "^"],
                  "group_depth": 2, "split_depth": 0})
    return D3


@pytest.fixture
def Bars():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [3, 3], "type": "trajectory",
                "split_depth": 0})

    D2 = sf.tbl.convert.AddColumn()
    D2.run([D1],
           {"col_info": [0, "x_pos", "float", "none", "Bar plot x pos"],
            "col_values": [0.9, 1.0, 1.1, 1.9, 2.0, 2.1, 2.9, 3.0, 3.1],
            "split_depth": 0})

    D3 = sf.fig.bar.Simple()
    D3.run([D2], {"calc_cols": ["x_pos", "trj_no"], "group_depth": 1,
                  "bar_widths": 0.1, "split_depth": 0})
    return D3


@pytest.fixture
def LinesError():
    D1 = sf.tbl.create.Index()
    D1.run([],
           {"index_counts": [3, 5], "type": "trajectory",
            "split_depth": 0})

    D2 = sf.trj.random.Walk2DCenter()
    D2.run([D1],
           {"diff_coeff": 0.1, "interval": 0.1, "n_step": 5,
            "length_unit": "um", "split_depth": 0})

    D2a = sf.trj.msd.Each()
    D2a.run([D2], {"group_depth": 2, "split_depth": 0})

    D2b = sf.tbl.stat.Mean()
    D2b.run([D2a], {"calc_col": "msd", "index_cols": ["img_no", "interval"],
                    "split_depth": 0})

    D3 = sf.fig.line.Simple()
    D3.run([D2b],
           {"calc_cols": ["interval", "msd"], "err_col": "sem",
            "group_depth": 1, "split_depth": 0})
    return D3


@pytest.fixture
def BarsError():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [3, 3], "type": "trajectory",
                "split_depth": 0})

    D2a = sf.tbl.convert.AddColumn()
    D2a.run([D1],
            {"col_info": [0, "x_pos", "float", "none", "Bar plot x pos"],
             "col_values": [0.9, 1.0, 1.1, 1.9, 2.0, 2.1, 2.9, 3.0, 3.1],
             "split_depth": 0})

    D2b = sf.tbl.convert.AddColumn()
    D2b.run([D2a],
            {"col_info": [0, "std", "float", "none", "Bar plot errorbar"],
             "col_values": [0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.1, 0.2, 0.3],
             "split_depth": 0})

    D3 = sf.fig.bar.Simple()
    D3.run([D2b], {"calc_cols": ["x_pos", "trj_no"], "group_depth": 1,
                   "err_col": "std", "bar_widths": 0.1, "split_depth": 0})
    return D3


def test_Basic_line(tmpdir, Lines):

    D = sf.fig.style.Basic()
    D.run([Lines],
          {"limit": [0, 1, 0, 1],
           "format": ["%.1f", "%.1f"]})
    D.save_data(D.data[0], os.path.join(tmpdir, "test.fig"))
    del D

    D = sf.fig.style.Basic()
    D.run([Lines],
          {"limit": [0, 1, 0, 1],
           "tick": [[0, 1], [0, 1]],
           "tick_label": [["0", "1"], ["0", "1"]],
           "is_box": True,
           "label": ["x-axis", "y-axis"],
           "line_styles": ["-", ":", "--"],
           "line_colors": [0, 0, 0],
           "marker_styles": "o",
           "marker_sizes": 2,
           "marker_colors": [[0, 0, 0], [255, 0, 0]],
           "marker_widths": 0.5,
           "format": ["%.1f", "%.1f"],
           "title": "title"})
    del D

    D = sf.fig.style.Basic()
    D.run([Lines],
          {"tick": [np.array([0, 1]), np.array([0, 1])],
           "is_box": False})
    assert len(D.data[0].axes[0].get_children()) == 13


def test_Basic_scatter(Scatters):
    D = sf.fig.style.Basic()
    D.run([Scatters],
          {"marker_sizes": 1,
           "marker_widths": 0.5,
           "marker_colors": [[0, 0, 0], [255, 0, 0]]})
    assert len(D.data[0].axes[0].get_children()) == 13
    del D

    D = sf.fig.style.Basic()
    D.run([Scatters], {"marker_colors": [[0, 0, 0], None]})
    assert len(D.data[0].axes[0].get_children()) == 13


def test_Basic_bar(Bars):

    D = sf.fig.style.Basic()
    D.run([Bars],
          {"bar_widths": 0.05,
           "marker_widths": 0.5,
           "marker_colors": [[0, 0, 0], [255, 0, 0]]})
    assert len(D.data[0].axes[0].get_children()) == 19
    del D

    D = sf.fig.style.Basic()
    D.run([Bars],
          {"marker_colors": [[0, 0, 0], None]})
    assert len(D.data[0].axes[0].get_children()) == 19


def test_Basic_line_error(LinesError):

    D = sf.fig.style.Basic()
    D.run([LinesError],
          {"line_styles": "--",
           "line_colors": [0, 0, 0],
           "marker_styles": "o",
           "marker_sizes": 2,
           "marker_colors": [[0, 0, 0], [255, 0, 0]],
           "marker_widths": 0.5,
           "error_thicknesses": 2,
           "error_line_styles": ":",
           "error_colors": [0, 0, 0],
           "error_cap_sizes": 0})
    assert len(D.data[0].axes[0].get_children()) == 22


def test_Basic_bar_error(BarsError):

    D = sf.fig.style.Basic()
    D.run([BarsError],
          {"line_styles": "--",
           "line_colors": [0, 0, 0],
           "marker_styles": "o",
           "marker_sizes": 2,
           "marker_colors": [[0, 0, 0], [255, 0, 0]],
           "marker_widths": 0.5,
           "error_thicknesses": 2,
           "error_line_styles": ":",
           "error_colors": [0, 0, 0],
           "error_cap_sizes": 0})
    assert len(D.data[0].axes[0].get_children()) == 28


def test_Basic_legend(Lines):
    D = sf.fig.style.Basic()
    D.run([Lines], {"legend": [None, None]})
    assert D.data[0].axes[0].legend_ is None
    del D

    D = sf.fig.style.Basic()
    D.run([Lines],
          {"legend": [["one", "two", "three"], None,
                      {"loc": "upper left"}]})
    assert type(D.data[0].axes[0].legend_) == mpl.legend.Legend
    del D

    D = sf.fig.style.Basic()
    D.run([Lines], {"legend": [["one", "two", "three"], [0, 1, 2]]})
    assert type(D.data[0].axes[0].legend_) == mpl.legend.Legend
    del D

    D = sf.fig.style.Basic()
    with pytest.raises(Exception) as e:
        D.run([Lines], {"legend": [["one", "two"], [0, 1, 2]]})

    D = sf.fig.style.Basic()
    D.run([Lines],
          {"legend": [None, [0, 1, 2]]})
    assert type(D.data[0].axes[0].legend_) == mpl.legend.Legend


def test_Basic_log(Lines):
    D = sf.fig.style.Basic()
    D.run([Lines], {"log_scale": [True, True]})
    assert len(D.data[0].axes[0].get_children()) == 13


def test_ParamTable_Lines():

    # Many line with errorbar
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [3, 5], "type": "trajectory",
                "split_depth": 0})

    D2 = sf.trj.random.Walk2DCenter()
    D2.run([D1],
           {"diff_coeff": 0.1, "interval": 0.1, "n_step": 5,
            "length_unit": "um", "split_depth": 0})

    D2a = sf.trj.msd.Each()
    D2a.run([D2], {"group_depth": 2, "split_depth": 0})

    D2b = sf.tbl.stat.Mean()
    D2b.run([D2a], {"calc_col": "msd", "index_cols": ["img_no", "interval"],
                    "split_depth": 1})

    D3 = sf.fig.line.Simple()
    D3.run([D2b],
           {"calc_cols": ["interval", "msd"], "err_col": "sem",
            "group_depth": 2, "split_depth": 1})

    D1a = sf.tbl.create.Index()
    D1a.run([], {"index_counts": [3], "type": "image", "split_depth": 0})

    D1b = sf.tbl.convert.AddColumn()
    D1b.run([D1a], {"col_info": [0, "limit", "str", "none", "fig limit"],
                    "col_values": ["[0, 1, 0, 1]", "[0, 1, 0, 2]",
                                   "[0, 1, 0, 3]"],
                    "split_depth": 0})

    D1c = sf.tbl.convert.AddColumn()
    D1c.run([D1b], {"col_info": [0, "tick", "str", "none", "fig tick"],
                    "col_values": ["[[0, 1], [0, 1]]", "[[0, 1], [0, 2]]",
                                   "[[0, 1], [0, 3]]"],
                    "split_depth": 0})
    D1d = sf.tbl.convert.AddColumn()
    D1d.run([D1c], {"col_info": [0, "tick_label", "str", "none",
                                 "fig tick label"],
                    "col_values": ["[['0', '1'], ['0', '1']]",
                                   "[['0', 'a'], ['0', 'b']]",
                                   "[['0', '1'], ['0', '3']]"],
                    "split_depth": 0})

    D1e = sf.tbl.convert.AddColumn()
    D1e.run([D1d], {"col_info": [0, "label", "str", "none",
                                 "fig label"],
                    "col_values": ["['x-axis1', 'y-axis1']",
                                   "['x-axis2', 'y-axis2']",
                                   "['x-axis3', 'y-axis3']"],
                    "split_depth": 0})

    D1f = sf.tbl.convert.AddColumn()
    D1f.run([D1e], {"col_info": [0, "format", "str", "none",
                                 "fig format"],
                    "col_values": ["['%.0f', '%.0f']",
                                   "['%.1f', '%.1f']",
                                   "['%.2f', '%.2f']"],
                    "split_depth": 0})

    D1g = sf.tbl.convert.AddColumn()
    D1g.run([D1f], {"col_info": [0, "line_widths", "str", "none",
                                 "fig line widths"],
                    "col_values": ["1", "2", "3"],
                    "split_depth": 0})

    D1h = sf.tbl.convert.AddColumn()
    D1h.run([D1g], {"col_info": [0, "line_styles", "str", "none",
                                 "fig line styles"],
                    "col_values": ["-", ":", "--"],
                    "split_depth": 0})

    D1i = sf.tbl.convert.AddColumn()
    D1i.run([D1h], {"col_info": [0, "line_colors", "str", "none",
                                 "fig line colors"],
                    "col_values": ["[100,0,0]", "[0,100,0]", "[0,0,0]"],
                    "split_depth": 0})

    D1j = sf.tbl.convert.AddColumn()
    D1j.run([D1i], {"col_info": [0, "marker_styles", "str", "none",
                                 "fig marker styles"],
                    "col_values": ["o", "^", "s"],
                    "split_depth": 0})

    D1k = sf.tbl.convert.AddColumn()
    D1k.run([D1j], {"col_info": [0, "marker_sizes", "str", "none",
                                 "fig marker sizes"],
                    "col_values": ["1", "2", "3"],
                    "split_depth": 0})

    D1l = sf.tbl.convert.AddColumn()
    D1l.run([D1k], {"col_info": [0, "marker_colors", "str", "none",
                                 "fig marker colors"],
                    "col_values": ["['umap_face', [100,0,0]]",
                                   "[[200,0,0], [200,0,0]]",
                                   "[[150,0,0], [150,0,0]]"],
                    "split_depth": 0})

    D1m = sf.tbl.convert.AddColumn()
    D1m.run([D1l], {"col_info": [0, "marker_widths", "str", "none",
                                 "fig marker widths"],
                    "col_values": ["1", "2", "3"],
                    "split_depth": 0})

    D1n = sf.tbl.convert.AddColumn()
    D1n.run([D1m], {"col_info": [0, "error_thicknesses", "str", "none",
                                 "fig error thickness"],
                    "col_values": ["1", "2", "3"],
                    "split_depth": 0})

    D1o = sf.tbl.convert.AddColumn()
    D1o.run([D1n], {"col_info": [0, "error_line_styles", "str", "none",
                                 "fig error_line_styles"],
                    "col_values": ["-", "--", ":"],
                    "split_depth": 0})

    D1p = sf.tbl.convert.AddColumn()
    D1p.run([D1o], {"col_info": [0, "error_colors", "str", "none",
                                 "fig eror colors"],
                    "col_values": ["'umap_face'",
                                   "[200,0,0]",
                                   "[150,0,0]"],
                    "split_depth": 0})

    D1q = sf.tbl.convert.AddColumn()
    D1q.run([D1p], {"col_info": [0, "error_cap_sizes", "str", "none",
                                 "fig error cap sizes"],
                    "col_values": ["1", "2", "3"],
                    "split_depth": 0})

    D1r = sf.tbl.convert.AddColumn()
    D1r.run([D1q], {"col_info": [0, "is_box", "str", "none",
                                 "fig is boxed"],
                    "col_values": ["True", "None", "False"],
                    "split_depth": 0})

    D1s = sf.tbl.convert.AddColumn()
    D1s.run([D1r], {"col_info": [0, "log_scale", "str", "none",
                                 "fig log scale"],
                    "col_values": ["[False, False]",
                                   "[True, False]", "[False, True]"],
                    "split_depth": 0})

    D1t = sf.tbl.convert.AddColumn()
    D1t.run([D1s], {"col_info": [0, "title", "str", "none",
                                 "fig title"],
                    "col_values": ["Title1", "title2", "TITLE3"],
                    "split_depth": 0})

    D4 = sf.tbl.convert.AddColumn()
    D4.run([D1t], {"col_info": [0, "legend", "str", "none",
                                "fig legend"],
                   "col_values": ["[None, [0]]",
                                  "[None, None]",
                                  "['line1']"],
                   "split_depth": 1})

    D5 = sf.fig.style.ParamTable()
    D5.run([D3, D4], {})
    assert len(D5.data[0].axes[0].get_children()) == 16


@pytest.fixture
def GrayScale():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [3], "type": "image",
                "split_depth": 0})

    D2 = sf.img.create.Black()
    D2.run([D1], {"pitch": 0.1, "interval": 0.1,
                  "img_size": [5, 5], "length_unit": "um",
                  "split_depth": 1})
    D2.data[0][0, 2, :] = np.array([0, 1, 2, 3, 4])
    D2.data[1][0, 2, :] = np.array([0, 1, 2, 3, 4])
    D2.data[2][0, 2, :] = np.array([0, 1, 2, 3, 4])

    D3 = sf.fig.image.Gray()
    D3.run([D2], {"lut_limits": [0, 4], "split_depth": 1})
    return D3


def test_ParamTable_colorscale(GrayScale):

    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [3, 5], "type": "trajectory",
                "split_depth": 0})

    D1a = sf.tbl.create.Index()
    D1a.run([], {"index_counts": [3], "type": "image", "split_depth": 0})

    D1b = sf.tbl.convert.AddColumn()
    D1b.run([D1a], {"col_info": [0, "clim", "str", "none", "fig clim"],
                    "col_values": ["[0,1]", "[0,2]", "[0,3]"],
                    "split_depth": 0})

    D4 = sf.tbl.convert.AddColumn()
    D4.run([D1b], {"col_info": [0, "cmap", "str", "none", "fig cmap"],
                   "col_values": ['hot', 'plasma', 'inferno'],
                   "split_depth": 1})

    D5 = sf.fig.style.ParamTable()
    D5.run([GrayScale, D4], {})
    assert len(D5.data[0].axes[0].get_children()) == 11


def test_ParamTable_Bars():

    # Many bars with errorbar
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [3, 5], "type": "trajectory",
                "split_depth": 0})

    D2 = sf.trj.random.Walk2DCenter()
    D2.run([D1],
           {"diff_coeff": 0.1, "interval": 0.1, "n_step": 5,
            "length_unit": "um", "split_depth": 0})

    D2a = sf.trj.msd.Each()
    D2a.run([D2], {"group_depth": 2, "split_depth": 0})

    D2b = sf.tbl.stat.Mean()
    D2b.run([D2a], {"calc_col": "msd", "index_cols": ["img_no", "interval"],
                    "split_depth": 1})

    D3 = sf.fig.bar.Simple()
    D3.run([D2b],
           {"calc_cols": ["interval", "msd"], "err_col": "sem",
            "group_depth": 2, "split_depth": 1})

    D1a = sf.tbl.create.Index()
    D1a.run([], {"index_counts": [3], "type": "image", "split_depth": 0})

    D4 = sf.tbl.convert.AddColumn()
    D4.run([D1a], {"col_info": [0, "bar_widths", "str", "none",
                                "fig bar width"],
                   "col_values": ["1",
                                  "1",
                                  "1"],
                   "split_depth": 1})

    D5 = sf.fig.style.ParamTable()
    D5.run([D3, D4], {})
    assert len(D5.data[0].axes[0].get_children()) == 19


@pytest.fixture
def Gray():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1], "type": "image",
                "split_depth": 0})

    D2 = sf.img.create.Black()
    D2.run([D1], {"pitch": 0.1, "interval": 0.1,
                  "img_size": [5, 5], "length_unit": "um",
                  "split_depth": 1})
    D2.data[0][0, 2, :] = np.array([0, 1, 2, 3, 4])

    D3 = sf.fig.image.Gray()
    D3.run([D2], {"lut_limits": [0, 4], "split_depth": 1})
    return D3


def test_ColorBar(Gray, Scatters):
    D = sf.fig.style.ColorBar()
    D.run([Gray], {"tick": [0, 1, 2, 3, 4], "format": "%0.1f"})
    assert len(D.data[0].axes[0].get_children()) == 11
    del D

    D = sf.fig.style.Basic()
    D.run([Gray], {"clim": [0, 1], "cmap": "hot"})
    assert len(D.data[0].axes[0].get_children()) == 11
    del D

    D = sf.fig.style.ColorBar()
    D.run([Gray], {"tick": [0, 1, 2, 3, 4],
                   "is_vertical": True, "format": "%0.1f"})
    assert len(D.data[0].axes[0].get_children()) == 11
    del D

    D = sf.fig.style.ColorBar()
    D.run([Scatters], {})
    assert len(D.data[0].axes[0].get_children()) == 13


@pytest.fixture
def GrayLabel():
    D1 = sf.tbl.create.Index()
    D1.run([], {"index_counts": [1], "type": "image",
                "split_depth": 0})

    D2 = sf.img.create.Black()
    D2.run([D1], {"pitch": 0.1, "interval": 0.1,
                  "img_size": [5, 5], "length_unit": "um",
                  "split_depth": 1})
    D2.data[0][0, 2, :] = np.array([0, 1, 2, 3, 4])

    D3 = sf.fig.image.Gray()
    D3.run([D2], {"lut_limits": [0, 4], "split_depth": 1,
                  "user_param": [["label", ["label1"], "list", "Label"]]})
    return D3


def test_ColorBar_label(GrayLabel):
    D = sf.fig.style.ColorBar()
    D.run([GrayLabel], {})
    assert len(D.data[0].axes[0].get_children()) == 11
