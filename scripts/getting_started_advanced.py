""" 
=============== CAUTION =======================================================

Run "pip install -r requirements-full.txt" before running this script.

===============================================================================
"""

import os
import urllib.request
import zipfile
import io

import slitflow as sf


root_dir = "slitflow_tutorial"
project_dir = os.path.join(root_dir, "getting_started_advanced")
data_root_dir = os.path.join(root_dir, "data")
data_dir = os.path.join(data_root_dir, "getting_started_advanced")

# Create directories
if not os.path.isdir(root_dir):
    os.makedirs(root_dir)
if not os.path.isdir(project_dir):
    os.makedirs(project_dir)
if not os.path.isdir(data_root_dir):
    os.makedirs(data_root_dir)
if not os.path.isdir(data_dir):
    os.makedirs(data_dir)


def preparation_download_movies():
    # Download single-molecule movies

    file_url = 'https://zenodo.org/record/7645485/files/getting_started_advanced.zip'

    opener = urllib.request.build_opener()

    # If you are in proxy environment, uncomment the following lines.
    # proxy_handler = urllib.request.ProxyHandler({
    #     'https': 'your_proxy_url:port'})
    # opener = urllib.request.build_opener(proxy_handler)

    print("Downloading single-molecule movies. This may take tens of minutes.")
    with opener.open(file_url) as download_file:
        with zipfile.ZipFile(io.BytesIO(download_file.read())) as zip_file:
            zip_file.extractall(data_root_dir)
    print("Download completed.")


def pipeline_1_load():

    PL = sf.manager.Pipeline(project_dir)

    pitch = 0.0710837445886793  # [um/pix]
    interval = 0.03333  # [s]

    for i in [1, 2, 3]:
        path = os.path.join(data_dir, "rpb1", "rpb1-" + str(i) + ".tif")
        PL.add(sf.load.tif.SplitFile(), 0, (1, 1), "rpb1", "raw",
               ["RPB1"], [], [],
               {"path": path, "length_unit": "um", "pitch": pitch,
                "interval": interval, "value_type": "uint8", "indexes": [i],
                "split_depth": 1})

    path = os.path.join(data_dir, "mask", "mask.tif")
    PL.add(sf.load.tif.SingleFile(), 0, (2, 1), "mask", "raw",
           ["RPB1"], [], [],
           {"path": path, "length_unit": "um", "pitch": pitch,
            "value_type": "uint8", "split_depth": 1})
    PL.save("pipeline_1_load")
    PL.run()


def pipeline_2_tracking():

    PL = sf.manager.Pipeline(project_dir)

    PL.add(sf.img.filter.DifferenceOfGaussian(), 3, (1, 2), None, "dog",
           ["RPB1"], [(1, 1)], [2],
           {"wavelength": 0.6, "NA": 1.4, "split_depth": 1})
    PL.add(sf.img.filter.LocalMax(), 3, (1, 3), None, "localmax",
           ["RPB1"], [(1, 2)], [2], {"split_depth": 1})
    PL.add(sf.loc.convert.LocalMax2Xy(), 3, (1, 4), None, "xy",
           ["RPB1"], [(1, 3)], [2], {"split_depth": 1})
    PL.add(sf.loc.mask.BinaryImage(), 2, (1, 5), None, "mask",
           ["RPB1"], [(1, 4), (2, 1)], [1, 1], {"split_depth": 1})
    PL.add(sf.tbl.filter.CutOffPixelQuantile(), 2, (1, 6), None, 'cutoff',
           ["RPB1"], [(1, 5)], [2],
           {"calc_col": "intensity", "cut_factor": 4, "split_depth": 1})
    PL.add(sf.loc.fit.Gauss2D(), 3, (1, 7), None, 'refine',
           ["RPB1"], [(1, 1), (1, 6)], [2, 2],
           {"half_width": 4, "split_depth": 1})
    PL.add(sf.trj.wtrackpy.Link(), 3, (1, 8), None, 'trj',
           ["RPB1"], [(1, 7)], [1], {"search_range": 0.8, "split_depth": 1})
    PL.add(sf.trj.filter.StepAtLeast(), 2, (1, 9), None, 'long',
           ["RPB1"], [(1, 8)], [1],
           {"step": 9, "group_depth": 2, "split_depth": 1})
    PL.add(sf.tbl.math.Centering(), 1, (1, 10), None, "center",
           ["RPB1"], [(1, 9)], [1],
           {"calc_cols": ["x_um", "y_um"], "group_depth": 1, "split_depth": 1})
    PL.save("pipeline_2_tracking")
    PL.run()


def pipeline_3_show_trajectory():

    PL = sf.manager.Pipeline(project_dir)

    PL.add(sf.fig.line.Simple(), 2, (3, 1), "show", "fig",
           ["RPB1"], [(1, 10)], [1],
           {"calc_cols": ["x_um", "y_um"], "group_depth": 2, "split_depth": 1})
    PL.add(sf.fig.style.Basic(), 2, (3, 2), None, "style",
           ["RPB1"], [(3, 1)], [1],
           {"size": [4, 4], "margin": [0, 0, 0, 0],
           "limit": [-14, 14, -14, 14], "tick": [[-15, 15], [-15, 15]],
            "is_box": True, "line_widths": 0.7,
            "split_depth": 1})
    PL.add(sf.fig.figure.ToTiff(), 2, (3, 3), None, "tif",
           ["RPB1"], [(3, 2)], [1],
           {"scalebar": [5, 0.05, 0.05, 2, [0, 0, 0]],
           "dpi": 300, "split_depth": 0})
    PL.add(sf.img.montage.RGB(), 0, (3, 4), None, "mtg",
           ["RPB1"], [(3, 3)], [0],
           {"grid_shape": [1, 3], "padding_width": 0, "split_depth": 0})
    PL.save("pipeline_3_show_trajectory")
    PL.run()


def pipeline_4_spot_on():

    PL = sf.manager.Pipeline(project_dir)

    PL.add(sf.trj.wfastspt.JumpLenDist(), 0, (4, 1), "spoton", "hist",
           ["RPB1"], [(1, 9)], [0],
           {"trj_depth": 2, "MaxJump": 0.8, "BinWidth": 0.01, "CDF": False,
           "TimePoints": 5, "split_depth": 2})
    PL.add(sf.trj.wfastspt.FitJumpLenDist2comp(), 0, (4, 2), None, "fit2",
           ["RPB1"], [(4, 1)], [0],
           {"lower_bound": [0.05, 0.0001, 0], "upper_bound": [25, 0.08, 1],
           "LocError": 0.035, "iterations": 3, "dZ": 0.700, "useZcorr": False,
            "init": [0.5, 0.003, 0.3], "split_depth": 0})
    PL.add(sf.trj.wfastspt.ModelJumpLenDist(), 0, (4, 3), None, "model",
           ["RPB1"], [(4, 1), (4, 2)], [0, 0],
           {"show_pdf": True, "split_depth": 2})

    PL.save("pipeline_4_spot_on")
    PL.run()


def pipeline_5_spot_on_figure():
    PL = sf.manager.Pipeline(project_dir)

    # path to figure style table
    path = os.path.join(data_dir, "param", "spoton_fig.csv")

    # all required Data should be split into fig unit.
    PL.add(sf.fig.bar.WithModel(), 2, (4, 4), None, "fig",
           ["RPB1"], [(4, 1), (4, 3)], [2, 2],
           {"calc_cols": ["jump_dist", "prob"],
           "model_cols": ["jump_dist", "prob"],
            "group_depth": 2, "group_depth_model": 2, "split_depth": 2})
    PL.add(sf.load.table.SingleCsv(), 0, (4, 5), None, "fig_param",
           ["RPB1"], [], [],
           {"path": path, "col_info": [
               [1, "is_cdf", "int32", "num", "Whether histogram is CD"],
               [2, "dt", "int32", "num", "Time difference of jump step"],
               [0, "legend", "str", "none", "Legend string"],
               [0, "marker_colors", "str", "none", "Edge and face colors"],
               [0, "line_colors", "str", "none", "Line colors"]],
            "split_depth": 2})
    PL.add(sf.fig.style.ParamTable(), 0, (4, 6), None, "fig_style",
           ["RPB1"], [(4, 4), (4, 5)], [2, 2],
           {"size": [6, 2], "margin": [0.9, 0.6, 0.1, 0.1],
           "label": ["Jump distance (\u03bcm)", "Probability"],
            "format": ["%.1f", "%.2f"],
            "limit": [-0.01, 0.85, -0.001, 0.05],
            "tick": [[0, 0.2, 0.4, 0.6, 0.8], [0, 0.02, 0.04]],
            "marker_widths": 0.2})
    PL.add(sf.fig.figure.ToTiff(), 0, (4, 7), None, "fig_tif",
           ["RPB1"], [(4, 6)], [1], {"split_depth": 0})
    PL.add(sf.img.montage.RGB(), 0, (4, 8), None, 'fig_mtg',
           ["RPB1"], [(4, 7)], [0],
           {"grid_shape": [4, 1], "padding_width": 0, "split_depth": 0})

    PL.save("pipeline_5_spot_on_figure")
    PL.run()


def pipeline_6_tramway():

    PL = sf.manager.Pipeline(project_dir)

    PL.add(sf.trj.wtramway.Tessellation(), 1, (5, 1), "tram", "tess",
           ["RPB1"], [(1, 10)], [1], {"method": "gwr", "split_depth": 1})
    PL.add(sf.trj.wtramway.Inference(), 0, (5, 2), None, "infer",
           ["RPB1"], [(5, 1)], [1], {"mode": "d"})
    PL.add(sf.trj.wtramway.MapPlot(), 2, (5, 3), None, "map",
           ["RPB1"], [(5, 1), (5, 2)], [1, 1],
           {"feature": "diffusivity", "param": {"unit": "std"}})
    PL.add(sf.fig.style.Basic(), 0, (5, 4), None, "fig_style",
           ["RPB1"], [(5, 3)], [1],
           {"size": [4, 4], "margin": [0, 0, 0, 0], "is_box": True,
           "limit": [-14, 14, -14, 14], "tick": [[-15, 15], [-15, 15]],
            "clim": [0, 0.06], "cmap": "coolwarm"})
    PL.add(sf.fig.figure.ToTiff(), 0, (5, 5), None, "fig_tif",
           ["RPB1"], [(5, 4)], [1],
           {"scalebar": [5, 0.05, 0.05, 2, [0, 0, 0]],
           "dpi": 300, "split_depth": 0})
    PL.add(sf.img.montage.RGB(), 0, (5, 6), None, 'fig_mtg',
           ["RPB1"], [(5, 5)], [0],
           {"grid_shape": [1, 3], "padding_width": 0, "split_depth": 0})
    PL.add(sf.fig.style.ColorBar(), 0, (5, 7), None, "colorbar",
           ["RPB1"], [(5, 4)], [1],
           {"tick": [0, 0.02, 0.04, 0.06], "format": "%0.2f"})
    PL.add(sf.fig.figure.ToTiff(), 0, (5, 8), None, "cb_tif",
           ["RPB1"], [(5, 7)], [1], {"split_depth": 1})

    PL.save("pipeline_6_tramway")
    PL.run()


def pipeline_7_flowchart():

    PL = sf.manager.Pipeline(project_dir)

    PL.load(["pipeline_1_load", "pipeline_2_tracking",
             "pipeline_3_show_trajectory", "pipeline_4_spot_on",
             "pipeline_5_spot_on_figure", "pipeline_6_tramway"])

    PL.make_flowchart("pipeline", "grp_ana", scale=(0.6, 1.8))


if __name__ == '__main__':
    # Script must be written inside the "if __name__ == '__main__'"part
    # when using multiprocessing.

    preparation_download_movies()
    pipeline_1_load()
    pipeline_2_tracking()
    pipeline_3_show_trajectory()
    pipeline_4_spot_on()
    pipeline_5_spot_on_figure()
    pipeline_6_tramway()
    pipeline_7_flowchart()
