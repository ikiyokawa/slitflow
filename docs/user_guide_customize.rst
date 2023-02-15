Customize
==============================

A new task can easily be added to Slitflow as a user-defined class. The first
approach is to define a class directly in the Python script or Jupyter
notebook inherited from a Slitflow Data class.

The script below defines a simple class in the executable script that adds one
to the value of the table column, a class object being directly connected to a
series of Data objects. This procedure does not enable user-defined classes to
be added to the pipeline and run; however, it helps with new prototype classes.

.. code-block:: python

   import slitflow as sf


   class AddOne(sf.tbl.table.Table):
      """Class should have brief description.
      """

      def set_info(self, param):
         self.info.copy_req(0)
         # this class should remove zero depth columns except for calc_col
         index_cols = self.info.get_column_name("index")
         self.info.delete_column(keeps=index_cols + [param["calc_col"]])
         # index column names are also required to specify which column should
         # be remained
         self.info.add_param(
               "index_cols", index_cols, "str", "Index column names")
         self.info.add_param(
               "calc_col", param["calc_col"], "str", "Column name to calculate")
         self.info.set_split_depth(param["split_depth"])

      @staticmethod
      def process(reqs, param):
         df = reqs[0].copy()
         df_result = df[param["index_cols"]].copy()
         df_result[param["calc_col"]] = df[param["calc_col"]].values + 1
         return df_result


   # --- script from here ---
   D1 = sf.tbl.create.Index()
   D1.run([], {"type": "trajectory", "index_counts": [1, 2], "split_depth": 0})
   D2 = sf.trj.random.Walk2DCenter()
   D2.run([D1], {"diff_coeff": 0.1, "interval": 0.1, "n_step": 2,
               "length_unit": "um", "seed": 1, "split_depth": 0})
   D3 = AddOne()
   D3.run([D2], {"calc_col": "x_um", "split_depth": 0})
   print(D3.data[0])
   #    img_no  trj_no  frm_no      x_um
   #         1       1       1  1.000000
   #         1       1       2  1.229717
   #         1       1       3  1.143202
   # ...

The second approach is to add a class as a module file to the user subpackage
folder of the Slitflow source code. This allows the user-defined class to be
added to the pipeline and incorporated within a reusable analysis workflow,
or to create a flowchart. The following example executes the AddOne class of
a template module saved as an example in a user subpackage.

.. code-block:: python

   PL = sf.manager.Pipeline("path_to_project_directory")
   obs_names = ["Sample1"]
   PL.add(sf.tbl.create.Index(), 0, (1, 1), 'group1', 'index',
         obs_names, [], [],
         {"type": "trajectory", "index_counts": [1, 2], "split_depth": 0})
   PL.add(sf.trj.random.Walk2DCenter(), 0, (1, 2), None, 'trj',
         obs_names, [(1, 1)], [0],
         {"diff_coeff": 0.1, "interval": 0.1, "n_step": 2,
         "length_unit": "um", "seed": 1, "split_depth": 0})
   PL.add(sf.user.template.AddOne(), 0, (1, 3), None, 'one',
         obs_names, [(1, 2)], [0],
         {"calc_col": "x_um", "split_depth": 0})
   PL.save("pipeline")
   PL.run()


For more useful user-defined module files, consider moving them to the dev
subpackage folder and pulling requests to the dev branch of the Slitflow
repository to share them among users.