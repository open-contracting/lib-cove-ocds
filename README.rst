Lib CoVE OCDS
=============

|PyPI Version| |Build Status| |Lint Status| |Coverage Status| |Python Version|

Command line
------------

Call ``libcoveocds`` and pass the filename of some JSON data.

::

   libcoveocds tests/fixtures/common_checks/basic_1.json

It will produce JSON data of the results to standard output. You can pipe this straight into a file to work with.

You can also pass ``--schema-version 1.X`` to force it to check against a certain version of the schema.

In some modes, it will also leave directory of data behind. The following options apply to this mode:

* Pass ``--convert`` to get it to produce spreadsheets of the data.
* Pass ``--output-dir output`` to specify a directory name (default is a name based on the filename).
* Pass ``--delete`` to delete the output directory if it already exists (default is to error)
* Pass ``--exclude`` to avoid copying the original file into the output directory (default is to copy)

(If none of these are specified, it will not leave any files behind)

Code for use by external users
------------------------------

The only code that should be used directly by users is the ``libcoveocds.config`` and ``libcoveocds.api`` modules.

Other code (in ``libcore``, ``lib``, etc.) should not be used by external users of this library directly, as the structure and use of these may change more frequently.


.. |PyPI Version| image:: https://img.shields.io/pypi/v/libcoveocds.svg
   :target: https://pypi.org/project/libcoveocds/
.. |Build Status| image:: https://github.com/open-contracting/lib-cove-ocds/workflows/CI/badge.svg
.. |Lint Status| image:: https://github.com/open-contracting/lib-cove-ocds/workflows/Lint/badge.svg
.. |Coverage Status| image:: https://coveralls.io/repos/github/open-contracting/lib-cove-ocds/badge.svg?branch=main
   :target: https://coveralls.io/github/open-contracting/lib-cove-ocds?branch=main
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/libcoveocds.svg
   :target: https://pypi.org/project/libcoveocds/


