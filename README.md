# Slitflow

**Slitflow** is a Python package that aims to construct a fully reproducible and universally accessible workflow for single-molecule analysis—namely, **S**ingle-molecule **L**ocalization-**I**ntegrated **T**rajectory analysis work**FLOW**.

**Slitflow** comprises a flexible Data class that executes a task and stores the resulting data. A Data object can be input to the next Data object, the network of Data objects forming the entire workflow of complex single-molecule analysis, from image pre-processing to publication-quality figure creation.

![Slitflow_architecture](docs/img/slitflow_architecture.png)

**Slitflow** was designed by considering users who developed analysis tools, validated multiple analysis methods, reproduced workflows without programming skills, and used the results without installing software.

Please see [documentation](https://slitflow.readthedocs.io/en/latest/) for more information about **Slitflow**.

## Installation
**Slitflow** can be installed from [PyPI](https://pypi.org/project/slitflow/).

```bash
pip install slitflow
```

## How to use

The simplest script to make an index table is as follows:

```Python
import slitflow as sf

D = sf.tbl.create.Index()
D.run([], {"type": "trajectory", "index_counts": [2, 2], "split_depth": 0})
print(D.data[0])
#  img_no  trj_no
#       1       1
#       1       2
#       2       1
#       2       2
```
Please see ["Getting Started Basic"](https://slitflow.readthedocs.io/en/latest/getting_started_basic.html) to overview the functionality by analyzing the trajectories of simulated random walks.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yumaitou/slitflow/blob/main/scripts/notebook/getting_started_basic.ipynb)

["Getting Started Advanced"](https://slitflow.readthedocs.io/en/latest/getting_started_advanced.html) demonstrated the integrity and flexibility of the workflow using 1) a cherry-picked tracking method combining popular tools and 2) various state-of-the-art analyses using [single-molecule movies](https://zenodo.org/record/7645485#.ZAWnix_P2Um).

![pipeline](docs/img/getting_started_advance_pipeline.png)

## Citing
If **Slitflow** was useful for your research, please consider citing the following our paper:

* Ito, Y., Hirose, M., and Tokunaga, M. (2023). Slitflow: A Python framework for single-molecule dynamics and localization analysis. SoftwareX 23, 101462. [10.1016/j.softx.2023.101462](https://doi.org/10.1016/j.softx.2023.101462) 

## Contributing
**Slitflow** welcomes any contributions such as bug reports, bug fixes, enhancements, and documentation improvements from interested individuals and groups.
Please see [documentation](https://slitflow.readthedocs.io/en/latest/develop.html#contributing).
All contributors to this project are expected to abide by our [code of conduct](https://github.com/yumaitou/slitflow/CODE_OF_CONDUCT.md).
## Licence
**Slitflow** is distributed under the [BSD 3-Clause License](https://github.com/yumaitou/slitflow/blob/main/LICENCE). 
