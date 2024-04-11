Install
=======

The ``knotpy`` package requires Python 3.12 or newer installed on your
system.

Before proceeding, ensure you have the most recent version of pip (the
Python package manager) installed. If not, please consult the `Pip
documentation <https://pip.pypa.io/en/stable/>`__ for instructions on
installing pip before proceeding further.

Install the released version
----------------------------

To install the current release of ``knotpy`` with pip, execute the
following command:

.. code:: bash

   pip install knotpy

Install the development version
-------------------------------

First, make sure that `Git <https://git-scm.com/>`__ is installed on
your system. Then run:

.. code:: bash

   git clone https://github.com/bgabrovsek/knotpy.git
   cd knotpy
   pip install -e .[dev]

Then, if you want to update the ``knotpy`` package, pull the latest
changes from the git repository by run the following command in the
project directory.

::

   git pull

Testing
-------

``knotpy`` package uses the Python ``pytest`` testing package. To learn
more, read the pytest documentation at their
`homepage <https://pytest.org>`__.