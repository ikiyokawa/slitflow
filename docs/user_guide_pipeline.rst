
Pipeline
====================
While the Python script and Jupyter notebook can be used to create an analysis
pipeline script by connecting a series of Data objects, Slitflow provides a
pipeline system for improving the workflow organization by standardizing the
data-exporting directory.

The Pipeline creates a hierarchy in the project directory—comprising group
folders and analysis subfolders—with each task corresponding to an analysis
subfolder. Individual Data objects are stored in units of observation linked
to file names throughout the subfolders.

Users select the folder location for the required and resulting data of the
task by specifying an address comprising a group number and an analysis number. After inputting the
additional parameters and observation names, the entire workflow is
constructed by adding Data classes to the pipeline. 

All analyses are performed for all observations by executing the pipeline
run() method as described below.

.. code-block:: python

   PL = sf.manager.Pipeline("path_to_project_directory")
   PL.add(sf.tbl.create.Index(), 0, (1, 1), 'group1', 'index',
         ["Observation1"], [], [],
         {"type": "trajectory", "index_counts": [2, 2], "split_depth": 0})
   PL.add(sf.trj.random.Walk2DCenter(), 0, (1, 2), None, 'trj',
         None, [(1, 1)], [0],
         {"diff_coeff": 0.1, "interval": 0.1, "n_step": 2,
         "length_unit": "um", "split_depth": 0})
   PL.run()

The created workflow can be output as a CSV file and reused for additional
observations, rewritten parameters for adjustment, or distributed to other
researchers. Researchers who receive the workflow file can execute a three-line
script, as shown below, to fully reproduce a complex analytical workflow.

.. code-block:: python

    import slitflow as sf
    PL = sf.manager.Pipeline("path_to_project_directory")
    PL.run("pipeline_filename")

The Data dependencies in the pipeline can also be used to create flowcharts,
as shown in the getting started section.

Run mode
-----------------------
The run mode is a pipeline argument that specifies split-file loading and
parallel computing. When adding a Data class to the pipeline, the run mode is
set to a value between zero and three.

Modes 0 and 1 read all split files into memory simultaneously before executing
the processing. Conversely, Modes 2 and 3 repeat the loading, processing, and
saving cycle for each split data.

Additionally, Modes 0 and 2 compute the data list sequentially using a single
process. Conversely, Modes 1 and 3 compute the elements of the data list in
parallel using different processes. Table 1 shows the features of the run
modes and tasks suitable for each mode.

.. csv-table:: Table 1. Features of the run modes and tasks suitable for each mode
   :header-rows: 1

   "Run mode",     "0",    "1",    "2",    "3"
   "Loading",    "at once",  "at once", "split",  "split"
   "Processing",   "single",  "multi", "single", "multi"
   "Optimal file size", "small", "small", "large",  "large"
   "Optimal calculation",   "light",  "heavy",  "light", "heavy"

**Mode 0** is used for the light processing of data or aggregation of all data.

**Mode 1** is used when the entire split data can be loaded into
memory simultaneously; however, individual processing is too heavy, and
parallel computation is preferred for each element of the data list.

**Mode 2** is used when the overall data are too large to load, but there is a
computational overhead in processing the data list, or when parallel
computation is used to process single split data.

**Mode 3** is used when big data are split and loaded and further parallel
computation is required.