# Slitflow

A Python framework for single-molecule dynamics and localization
analysis.

## Installation
**Slitflow** can be installed from PyPI.

```bash
pip install slitflow
```

## How to use

```Python
import slitflow as sf

D = sf.tbl.create.Index()
D.run([],{"type": "trajectory", "index_counts": [1, 2], "split_depth": 0})
print(D.data[0])
```

## Licence
**Slitflow** is distributed under the BSD 3-Clause License. 

