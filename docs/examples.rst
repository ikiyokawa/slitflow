===============
Examples
===============

This section contains example pipelines to introduce the functionality of 
**Slitflow**.

MSD analysis
===================
This example simulates confined random walk in circular regions.
The Ensemble-Averaged MSDs are fitted with the confined model and the
parameters are statistically compared between different region sizes and
diffusivity.

.. code-block:: Python
    
    # make a project directory (in the user directory)
    prj_dir = os.path.join(os.path.expanduser("~"), "slitflow", "example_msd_analysis")
    PL = sf.manager.Pipeline(prj_dir)

    n_trj = 100
    n_step = 19
    interval = 0.1
    diffusion_names = ["Slow", "Medium", "Fast"]
    diffusion_coeffs = [0.1, 0.2, 0.4]
    radius_names = ["Narrow", "Wide"]
    radius_vals = [1, 2]
    rep_names = ["rep1", "rep2", "rep3"]

    obs_names = []
    params = []
    for diffusion_name, diffusion_coeff in zip(
            diffusion_names, diffusion_coeffs):
        for radius_name, radius_val in zip(radius_names, radius_vals):
            for rep_name in rep_names:
                obs_names.append(diffusion_name + "_" +
                                 radius_name + "_" + rep_name)
                params.append([diffusion_coeff, radius_val])

    # simulate confined random walk
    for obs_name, param in zip(obs_names, params):
        PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj", "index",
               [obs_name], [], [],
               {"type": "trajectory", "index_counts": [1, n_trj], "split_depth": 0})
        PL.add(sf.trj.random.WalkCircle(), 0, (1, 2), None, "trj",
               [obs_name], [(1, 1)], [0],
               {"dimension": 2, "length_unit": "um", "diff_coeff": param[0],
               "interval": interval,
                "n_step": n_step, "radius": param[1], "offset": [3, 3], "split_depth": 0})

    # show trajectories
    PL.add(sf.fig.trajectory.All(), 0, (1, 3), None, "fig",
           None, [(1, 2)], [1], {"trj_depth": 2, "split_depth": 1})
    PL.add(sf.fig.trajectory.StyleAll(), 0, (1, 4), None, "stl",
           None, [(1, 3)], [1], {"limit": [0, 6, 0, 6]})
    PL.add(sf.fig.figure.ToTiff(), 0, (1, 5), None, "img",
           None, [(1, 4)], [1], {"split_depth": 0})
    PL.add(sf.img.convert.Obs2DepthRGB(), 0, (1, 6), None, "mrg",
           obs_names, [(1, 5)] * 18, [0] * 18,
           {"obs_name": "Trajectory", "split_depth": 0})
    PL.add(sf.img.montage.RGB(), 0, (1, 7), None, "mtg",
           None, [(1, 6)], [0], {"grid_shape": (3, 6), "padding_width": 10,
                                 "split_depth": 0})

    # calculate and fit MSD
    PL.add(sf.trj.msd.Each(), 0, (2, 1), "msd", 'msd',
           None, [(1, 2)], [0],
           {"group_depth": 2, "split_depth": 0})
    PL.add(sf.tbl.stat.Mean(), 0, (2, 2), None, 'avemsd',
           None, [(2, 1)], [0],
           {"calc_col": "msd", "index_cols": ["interval"], "split_depth": 0})
    PL.add(sf.trj.msd.FitConfSaxton(), 0, (2, 3), None, "fit",
           None, [(2, 2)], [0],
           {"step": 19, "group_depth": 0, "split_depth": 0})
    PL.add(sf.trj.msd.ModelConfSaxton(), 0, (2, 4), None, "model",
           None, [(2, 3)], [0],
           {"x_lims": [0, 2], "step": 0.01, "group_depth": 0,
           "split_depth": 0})
    PL.add(sf.fig.line.WithModel(), 0, (2, 5), None, "fig",
           None, [(2, 2), (2, 4)], [0, 0],
           {"calc_cols": ["interval", "msd"], "err_col": "sem",
           "model_cols": ["interval", "model"], "group_depth": 0,
            "group_depth_model": 0, "split_depth": 0})
    PL.add(sf.fig.style.Basic(), 0, (2, 6), None, 'stl',
           None, [(2, 5)], [0],
           {"limit": [-0.05, 2.05, -0.01, 2.25],
           "tick": [[0, 0.5, 1, 1.5, 2], [0, 0.5, 1, 1.5, 2]],
            "label": ["Interval (s)", "MSD (\u03bcm$^{2}$)"],
            "format": ['%.1f', '%.1f'],
            "marker_size": 1, "line_colors": [[180, 0, 180]],
            "marker_colors": [[[0, 0, 0]], [None]]})
    PL.add(sf.fig.figure.ToTiff(), 0, (2, 7), None, 'img',
           None, [(2, 6)], [0], {"split_depth": 0})
    PL.add(sf.img.convert.Obs2DepthRGB(), 0, (2, 8), None, "mrg",
           obs_names, [(2, 7)] * 18, [0] * 18,
           {"obs_name": "Trajectory", "split_depth": 0})
    PL.add(sf.img.montage.RGB(), 0, (2, 9), None, "mtg",
           None, [(2, 8)], [0], {"grid_shape": (3, 6), "padding_width": 10,
           "split_depth": 0})

    # parameter statistics
    diff_rad_names = []
    for diffusion_name in diffusion_names:
        for radius_name in radius_names:
            diff_rad_name = diffusion_name + "_" + radius_name
            rep_obs_names = []
            for rep_name in rep_names:
                rep_obs_names.append(
                    diff_rad_name + "_" + rep_name)
            PL.add(sf.tbl.convert.Obs2Depth(), 0, (3, 1), "stat", "rep",
                   rep_obs_names, [(2, 3)] * 3, [0] * 3,
                   {"col_name": "rep_no",
                   "col_description": "Replicate number",
                    "obs_name": diff_rad_name, "split_depth": 0})
            diff_rad_names.append(diff_rad_name)

    PL.add(sf.tbl.convert.Obs2Depth(), 0, (3, 2), None, "param",
           diff_rad_names, [(3, 1)] * 6, [0] * 6,
           {"col_name": "obs_no",
            "col_description": "Observation number",
            "obs_name": "Parameters", "split_depth": 0})
    PL.add(sf.tbl.stat.Mean(), 0, (3, 3), None, "d_mean",
           None, [(3, 2)], [0],
           {"calc_col": "diff_coeff", "index_cols": ["obs_no"],
           "split_depth": 0})
    PL.add(sf.tbl.stat.Test(), 0, (3, 3), None, "d_test",
           None, [(3, 2)], [0],
           {"sample_col": "obs_no",
            "replicate_col": "rep_no",
            "calc_col": "diff_coeff", "split_depth": 0})
    PL.add(sf.fig.bar.Simple(), 0, (3, 5), None, "d_fig",
           None, [(3, 3)], [0],
           {"calc_cols": ["obs_no", "diff_coeff"],
            "err_col": "std", "group_depth": 0, "split_depth": 0})
    PL.add(sf.fig.style.Basic(), 0, (3, 6), None, "d_style",
           None, [(3, 5)], [0],
           {"size": [6.5, 4.5],
            "limit": [None, None, 0, 0.51],
            "tick": [[1, 2, 3, 4, 5, 6], [0, 0.1, 0.2, 0.3, 0.4, 0.5]],
            "tick_label": [
                ["Slow/\nNarrow", "Slow/\nWide",
                 "Medium/\nNarrow", "Medium/\nWide",
                 "Fast/\nNarrow", "Fast/\nWide"], None],
            "label": [None, "Diffusion coefficient (\u03bcm$^{2}$/s)"],
            "format": [None, '%.1f']})
    PL.add(sf.fig.figure.ToTiff(), 0, (3, 7), None, "d_tif",
           None, [(3, 6)], [0], {"split_depth": 0})

    PL.add(sf.tbl.stat.Mean(), 0, (3, 8), None, "r_mean",
           None, [(3, 2)], [0],
           {"calc_col": "r", "index_cols": ["obs_no"],
           "split_depth": 0})
    PL.add(sf.tbl.stat.Test(), 0, (3, 9), None, "r_test",
           None, [(3, 2)], [0],
           {"sample_col": "obs_no",
            "replicate_col": "rep_no",
            "calc_col": "r", "split_depth": 0})
    PL.add(sf.fig.bar.Simple(), 0, (3, 10), None, "r_fig",
           None, [(3, 8)], [0],
           {"calc_cols": ["obs_no", "r"],
            "err_col": "std", "group_depth": 0, "split_depth": 0})
    PL.add(sf.fig.style.Basic(), 0, (3, 11), None, "r_style",
           None, [(3, 10)], [0],
           {"size": [6.5, 4.5],
            "limit": [None, None, 0, 2.55],
            "tick": [[1, 2, 3, 4, 5, 6], [0, 0.5, 1, 1.5, 2, 2.5]],
            "tick_label": [
                ["Slow/\nNarrow", "Slow/\nWide",
                 "Medium/\nNarrow", "Medium/\nWide",
                 "Fast/\nNarrow", "Fast/\nWide"], None],
            "label": [None, "Confinement radius (\u03bcm)"],
            "format": [None, '%.1f']})
    PL.add(sf.fig.figure.ToTiff(), 0, (3, 12), None, "d_tif",
           None, [(3, 11)], [0], {"split_depth": 0})

    PL.run()


Particle movie simulation
==========================
This example simulates single-molecule movies. Bright spots are represented as
two-dimensional Gaussian spots, and Gaussian noise is added to each pixel.

.. code-block:: Python
    
    # make a project directory (in the user directory)
    prj_dir = os.path.join(
       os.path.expanduser("~"), "slitflow", "example_particle_movie_simulation")
    PL = sf.manager.Pipeline(prj_dir)

    PL.add(sf.tbl.create.Index(), 0, (1, 1), "trj", "index",
           ["Particles"], [], [],
           {"type": "trajectory", "index_counts": [3, 10], "split_depth": 0})
    PL.add(sf.trj.random.WalkRect(), 0, (1, 2), None, "trj",
           None, [(1, 1)], [0],
           {"dimension": 2, "length_unit": "um", "diff_coeff": 0.1,
            "interval": 0.1,
            "n_step": 99, "lims": [[1, 9], [1, 9]], "split_depth": 0})
    PL.add(sf.tbl.convert.SortCols(), 0, (1, 3), None, 'loc',
           None, [(1, 2)], [0],
           {"new_depths": [1, 3, 2], "split_depth": 1})
    PL.add(sf.img.plot.Gauss2D(), 2, (2, 1), "movie", "gauss",
           None, [(1, 3)], [1],
           {"pitch": 0.1, "sd": 0.2, "img_size": [100, 100],
           "window_factor": 3, "group_depth": 2, "split_depth": 1})
    PL.add(sf.img.noise.Gauss(), 2, (2, 2), None, "noise",
           None, [(2, 1)], [1],
           {"sigma": 0.001, "baseline": 1, "split_depth": 1})
    PL.run()