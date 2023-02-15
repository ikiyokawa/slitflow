
Data
====================
To create an analysis workflow using Slitflow, users must write all tasks as
subclasses of the Data class, which is the basic unit of a data-processing
pipeline. The Data class is categorized based on the resulting data type—such
as the NumPy array for image data and the Pandas DataFrame for table data.

Slitflow provides various Data classes, including data loading, image
processing, trajectory analysis, localization analysis, and figure creation.
Users can find a Data class that fits their purpose from the API documentation.
Users can also create a user-defined Data class by temporarily defining it in
script code or creating a submodule file in the user subpackage. 

The data class has the following structure to ensure scalability in data
splitting, parallel processing, and workflow reuse:

process()
---------------------------
The Data class has a static process() method that is directly accessible
without creating a Data object. This structure enables users to execute any
task independently of the workflow as follows:

.. code-block:: python

   # after preparing inputs and parameters then
   import slitflow as sf
   result = sf.module_name.ClassName.process(inputs, parameters)

The process() method requires input data and a parameter dictionary. The input
data comprises a list of actual data directly used in the analysis. Each list
element corresponds to the result of a different Data object when the
process() is called from the pipeline.

The following script creates the x and y coordinates of a two-dimensional
random walk. This class requires an index table to add trajectories—such as
images and trajectory numbers. This class also requires the diffusion
coefficient, time interval, total trajectory length, and column names of the
coordinates. The required input data and parameters can be found in the API
reference in the software documentation.

.. code-block:: python

   # prepare input data
   input_data = [pd.DataFrame({'img_no':[1, 1, 2, 2], 'trj_no':[1, 2, 1, 2]})]

   # prepare a parameter dictionary
   param = {'diff_coeff':0.1, 'interval':0.1, 'n_step':2,
            'calc_cols': ['x_um', 'y_um']}

   result = sf.trj.random.Walk2DCenter.process(reqs, param)
   print(result)
   #  img_no  trj_no  frm_no      x_um      y_um
   #       1       1       1  0.000000  0.000000
   #       1       1       2  0.070246  0.091597
   #       1       1       3  0.050692  0.306986
   #       1       2       1  0.000000  0.000000
   #       1       2       2 -0.033114  0.223334
   #       1       2       3 -0.066226  0.331866
   #       2       1       1  0.000000  0.000000
   #       2       1       2 -0.066394 -0.065537
   #       2       1       3  0.010336 -0.131401
   #       2       2       1  0.000000  0.000000
   #       2       2       2  0.034219 -0.243940
   #       2       2       3 -0.236360 -0.323460

run()
-----------------------
The static process() method is executed from the run() method if the users
create a Data object for the analysis workflow. The resulting data are stored
in the data property of the object. The run() method requires a list of Data
objects as input, instead of the raw data required for the static process()
method. 

The following code executes the random walk calculation as a Data object. The
input DataFrame is replaced with an index data object, which creates a table
of nested indices.

.. code-block:: python

   D1 = sf.tbl.create.Index()
   D1.run([], {'index_counts': [2, 2], 'type': 'trajectory', 'split_depth': 0})

   D2 = sf.trj.random.Walk2DCenter()
   D2.run([D1], {'diff_coeff': 0.1, 'interval': 0.1, 'n_step':2,
               'length_unit':'um','split_depth':0})
   print(D2.data[0])
   # the result is the same as above snippet

Info and Index
------------------------------------
The run() method executes not only the process() but also other preparation
steps—including adding parameter descriptions, creating a data index, and
pairing different input data. Information about the parameters and the
resulting data structure is stored in the info property of the Data object.
This information is exported as a JSON text file that can be read by
non-software users.

The Data object also contains a table of data hierarchies—such as images and
trajectory numbers. This table is used to pair different input data types and
identify the selected images and trajectories.

The following code snippet shows the information and index of the above random
walk calculation Data object.

.. code-block:: python

   print(D2.info.to_string())  # output is truncated
   # {"column": [
   #    {"depth": 1, "name": "img_no", "type": "int32",
   #     "unit": "num", "description": "Image number"}, ... ],
   #  "param": [
   #    {"name": "index_counts", "value": [2, 2],
   #     "unit": "num", "description": "Total counts of each column"}, ... ],
   #  "meta":
   #    {"version": "0.0.2",
   #     "class": "slitflow.trj.random.Walk2DCenter",
   #     "description": "Create X,Y-coordinate of two-dimensional random walk.",
   #     "datetime": "2023/01/06 14:50:59", "path": null,
   #     "reqs": {"req_0": {"column": [{"depth": 1, "name": "img_no", ...

   print(D2.info.index)
   #  img_no  trj_no  frm_no  _file  _split
   #       1       1       1      0       0
   #       1       1       2      0       0
   #       1       1       3      0       0
   #       1       2       1      0       0
   # ...

Split depth
-----------------------
The data to be analyzed have a hierarchical structure—for example, the
trajectory number, image number, replication number, and observation number.
When applying analysis to data or dividing and saving data, it is necessary to
specify the hierarchy in which the analysis or saving is to be performed.

Slitflow allows users to change the target hierarchy of tasks easily by
specifying the split depth. For example, users can calculate the average
coordinates for each trajectory and output them in a single DataFrame.

Using the same input, users can also average the trajectory coordinates for
each image and export them to a DataFrame for each image by changing only the
split depth. 

Additionally, users can use run_mp() instead of run() to compute
the split data using multiple processes, which accelerates the calculation
process by means of parallel computing.

.. code-block:: python

   D2.set_split(2)
   D3 = sf.tbl.stat.Mean()
   D3.run([D2], {"calc_col": "x_um", "split_depth": 0})
   print(D3.data)
   # [  img_no  trj_no      x_um       std       sem  count       sum
   #         1       1  0.040313  0.036255  0.020932      3  0.120938
   #         1       2 -0.033114  0.033113  0.019118      3 -0.099341
   #         2       1 -0.018686  0.041638  0.024040      3 -0.056058
   #         2       2 -0.067380  0.147337  0.085065      3 -0.202141]

   D2.set_split(1)
   D3 = sf.tbl.stat.Mean()
   D3.run([D2], {"calc_col": "x_um", "split_depth": 1})
   print(D3.data)
   # [  img_no      x_um       std       sem  count       sum
   #         1    0.0036  0.050811  0.020744      6  0.021598,
   #    img_no      x_um       std       sem  count       sum
   #         2 -0.043033   0.10044  0.041004      6 -0.258199]



Save and load
-----------------------
The resulting data are exported to the file format to which the Data class
belongs by simply executing the save() method for the Data object. The data
are divided into files according to specified split depths. Indexes—such as
the image and trajectory numbers of all split data—can be viewed in the text
file exported with the resulting data, in which the data hierarchy is
described.

