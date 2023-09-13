==========
About
==========

* **Slitflow** is developed in `https://github.com/yumaitou/slitflow/ <https://github.com/yumaitou/slitflow/>`_.
* The documentation can be found at `https://slitflow.readthedocs.io <https://slitflow.readthedocs.io>`_.
* **Slitflow** can be installed from `https://pypi.org/project/slitflow/ <https://pypi.org/project/slitflow/>`_.

Citation
==================

If **Slitflow** was useful for your research, please consider citing the following our paper:

* Ito, Y., Hirose, M., and Tokunaga, M. (2023). Slitflow: A Python framework for single-molecule dynamics and localization analysis. SoftwareX 23, 101462. `10.1016/j.softx.2023.101462 <https://doi.org/10.1016/j.softx.2023.101462>`_.


Environments
==================

**Slitflow** is tested on the following operating systems.

* Windows10
* Windows11 
* macOS Ventura 13
* Ubuntu 22.04.1

Dependencies
==================

The basic **slitflow** has the following dependencies:

* numpy
* pandas
* matplotlib
* tifffile
* tqdm
* psutil
* opencv-python
* scipy
* scikit-learn
* scikit-image

License
==================
**Slitflow** is distributed under the BSD 3-Clause License. 

.. code-block:: text

   BSD 3-Clause License

   Copyright (c) 2022-2023, Yuma Ito and contributors

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this
      list of conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

   3. Neither the name of the copyright holder nor the names of its
      contributors may be used to endorse or promote products derived from
      this software without specific prior written permission.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
   CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Changelog
=============
**Slitflow** follows major version zero (rapid development) of Semantic Versioning.

0.1.4 (Unreleased)
----------------------

Features
  * Added :class:`slitflow.trj.subtrj.Subtrajectory` class.
  * Updated the citation.
  * Improved API documentation.
  * Added the ``type`` parameter to :class:`slitflow.img.noise.Gauss` class.

API changes
  * Updated :class:`slitflow.tbl.convert.SortCols` to be able to sort all columns, resulting in a change in the process parameters.   

----

0.1.3 (2023-06-02)
----------------------

API changes
  * Renamed ``slitflow.info.Info.to_string()`` to :meth:`slitflow.info.Info.to_json`.

----

0.1.2 (2023-05-19)
----------------------

Features
  * Updated getting started for Gitpod and Colab.
  * Updated requirements.
  * Added :class:`slitflow.tbl.proc.SelectParam` class.
  * Added :class:`slitflow.img.proc.SelectParam` class.
  * Added :class:`slitflow.img.create.CheckerBoard` class.

API changes
  * Changed :class:`slitflow.img.create.Black` class parameters.

Bug fixes
    * Fixed bug related to :class:`slitflow.img.proc.SelectParam` class. See "Add SelectParam and fix related bugs" commit.
    * Fixed bug in :class:`~slitflow.trj.wfastspt.ModelJumpLenDist` creating table indices inappropriately. 

----

0.1.1 (2023-03-07)
----------------------

Features
  * Updated the documentation.
  * Added :class:`slitflow.img.noise.Gauss` class.
  * Added tests using pytest.
  * Added example scripts.

API changes
  * Changed to Python <3.11 due to dependency on scikit-image.

Bug fixes
  * Fixed bug in :class:`~slitflow.fig.figure.ToTiff` raising ValueError related
    to matplotlib.Figure.canvas.draw on macOS backend.
  * Fixed bug in :class:`~slitflow.manager.Pipeline.set_grp_name` related to
    loading CSV files.
  * Fixed bug related to splitting depth in figure classes.
  * Fixed bug in :class:`~slitflow.img.image.Image` splitting data inappropriately.

Identified issues
  * Bug in the drawing figure, probably caused by matplotlib figure refresh.
  * :class:`slitflow.img.plot.Gauss2D` requires specific split depth of reqs data.

----

0.1.0 (2023-02-02)
----------------------

Features
  * Added basic functionality.

----

0.0.1 (2022-10-29)
----------------------

Features
  * Added test code.