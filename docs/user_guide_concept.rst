
Concepts
====================
Slitflow is a Python package that aims to construct a fully reproducible and
universally accessible workflow for single-molecule analysis. To achieve this
goal, Slitflow comprises a flexible Data class that executes a task and stores
the resulting data. A Data object can be input to the next Data object, the
network of Data objects forming the entire workflow of complex single-molecule
analysis, from image pre-processing to publication-quality figure creation
. This architecture was designed to realize four different levels of
reproducibility and accessibility for the three workflow elements described
below.

Reproducibility
-----------------------
An ideal reproducible workflow should obtain the same results without
additional processing or parameter completion based on the reproducer's
intentions, independent of the computing environment. Slitflow focuses on
four aspects that tend to result in low reproducibility in single-molecule
analyses.

- **Task** : Slitflow requires the creation of a Data class for any trivial
  task. This includes selecting and sorting the data, performing simple
  arithmetic operations, and changing the line thickness of the resulting
  figures.
- **Parameter** : All parameters required for processing are entered each
  time as a dictionary of names and value sets. These parameters are exported
  along with the results and reused during reproduction. They are also
  readable by non-software users with accompanying parameter descriptions.
- **Pipeline** : All data classes used in the workflow, their parameters, and
  dependencies of the resulting data are described as pipeline scripts in the
  CSV file. Users can quickly reproduce, modify, and distribute the pipelines.
- **Environment** : Slitflow is written in Python, is freely available, and
  can be used in Windows, MacOS, and Linux operating system environments.
  Users can run the analysis on computers with small memory capacities or
  large multithreaded computers by simply changing the loading and processing
  unit size to suit their computing environment.

Accessibility
--------------------------
Inaccessible black-boxed analysis methods and intermediate results may
prevent workflow validation and expansion. Slitflow aims to build an open
workflow by designing access means for the following three elements:

- **Process** : Individual tasks can be run independently of the workflow and
  used as functions in user scripts to evaluate the functionality or implement
  it in their own algorithms.
- **Format** : Slitflow does not recommend creating proprietary data formats.
  An ideal data format should be opened and interpreted by humans using a
  standard application initially installed on an operating system. If this is
  difficult, Slitflow recommends creating a Data class that converts the
  format into images, tables, or text for viewing.
- **Result** : The Slitflow pipeline maps all Data classes to the resulting
  folders. All tasks are based on loading the required data file and saving
  the resulting file in a subfolder. This system allows users to access and
  examine all the intermediate data of any task in the workflow.









