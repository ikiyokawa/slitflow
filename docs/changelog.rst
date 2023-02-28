=============
Changelog
=============
**Slitflow** follows major version zero (rapid development) of Semantic Versioning.

0.1.1 (Not released)
====================

Features
--------------------

* Updated the documentation.
* Added :class:`slitflow.img.noise.Gauss` class.

API changes
--------------------

* Changed to Python <3.11 due to dependency on scikit-image.

Bug fixes
--------------------

* Fixed bug in :class:`~slitflow.fig.figure.ToTiff` raising ValueError related
  to matplotlib.Figure.canvas.draw on macOS backend.
* Fixed bug in :class:`~slitflow.manager.Pipeline.set_grp_name` related to
  loading CSV files.
* Fixed bugs related to splitting depth in figure classes.


Identified issues
--------------------

* Bug in the drawing figure, probably caused by matplotlib figure refresh.
* :class:`slitflow.img.plot.Gauss2D` requires specific split depth of reqs data.

----

0.1.0 (2023-02-02)
====================

Features
--------------------

* Added basic functionality.

----

0.0.1 (2022-10-29)
====================

Features
--------------------

* Added test code.