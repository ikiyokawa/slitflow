import os

import slitflow as sf

if __name__ == '__main__':  # This line is needed if multiprocessing is used.

    # make a project directory (in the user directory)
    root_dir = "slitflow_tutorial"
    project_dir = os.path.join(root_dir, "examples_particle_movie_simulation")

    # Create directories
    if not os.path.isdir(root_dir):
        os.makedirs(root_dir)
    if not os.path.isdir(project_dir):
        os.makedirs(project_dir)

    PL = sf.manager.Pipeline(project_dir)

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
