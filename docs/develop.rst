================
Development
================

Contributing
================
**Slitflow** welcomes any contributions such as bug reports, bug fixes, 
enhancements, and documentation improvements from interested individuals and 
groups. All contributors to this project are expected to abide by our 
`code of conduct <https://github.com/yumaitou/slitflow/CODE_OF_CONDUCT.md>`_.

You can contribute by creating a GitHub issue, pull request, and direct email 
to the author (<yitou@bio.titech.ac.jp>). Before submitting a contribution, 
check that you are using the latest version of **Slitflow**.

  .. _detailed-installation:

Installation
======================
Installation from pip includes only minimal dependencies. It is recommended to
add the package when an import error occurs in the execution of the class.
Alternatively, you can install everything from the requirement-full.txt file
in the GitHub repository.

.. code-block:: bash

    pip install -r requirement-full.txt

Dependencies for developers, including test, linter, and documentation, can be
installed as follows.

.. code-block:: bash

    pip install -r requirement-dev.txt

Bug report
================================
If you experience bugs using **Slitflow**, please open an issue on 
Github `Issue Tracker <https://github.com/yumaitou/slitflow/issue>`_. 
Please ensure that your bug report includes:

* The environment information, including the operating system and version numbers of Python and involved packages.
* A description of the behavior of the issue you encountered.
* A short reproducible code snippet or the steps you took to reproduce the bug.
* The entire error message, if applicable.

Pull request
========================
You can fix bugs, improve codes, and implement new features by creating a pull request to the GitHub **Slitflow** repository. To submit your pull request, please check that it meets the following guidelines:

1. Fork the `yumaitou/slitflow` repository.
2. Create a feature branch from `main`.
3. Create your codes in accordance with PEP 8 style guide. We recommend using an automated formatter such as `flake8`.
4. Create documentation of the new class or function by adding a structured docstring with Sphinx google style format.
5. Add test function in the tests directory using `pytest`. All lines of the new code should be tested to keep full code coverage. Run the whole test suite and ensure that all tests pass.
6. Commit your changes to the feature branch and push to GitHub forked repository.
7. Issue the pull request.

Documentation
========================
**Slitflow** uses Sphinx to generate the documentation.
API documentation is compiled automatically from source code docstrings using 
`autodoc`. **Slitflow** uses google style docstrings.