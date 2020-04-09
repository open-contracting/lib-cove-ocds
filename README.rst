Lib CoVE OCDS
=============

|PyPI Version| |Build Status| |Lint Status| |Coverage Status| |Python Version|

Command line
------------

Call ``libcoveocds`` and pass the filename of some JSON data.

::

   libcoveocds tests/fixtures/common_checks/basic_1.json

Code for use by external users
------------------------------

The only code that should be used directly by users is the ``libcoveocds.config`` and ``libcoveocds.api`` modules.

Other code (in ``libcore``, ``lib``, etc.) should not be used by external users of this library directly, as the structure and use of these may change more frequently.


.. |PyPI Version| image:: https://img.shields.io/pypi/v/libcoveocds.svg
   :target: https://pypi.org/project/libcoveocds/
.. |Build Status| image:: https://github.com/open-contracting/lib-cove-ocds/workflows/CI/badge.svg
.. |Lint Status| image:: https://github.com/open-contracting/lib-cove-ocds/workflows/Lint/badge.svg
.. |Coverage Status| image:: https://coveralls.io/repos/github/open-contracting/lib-cove-ocds/badge.svg?branch=master
   :target: https://coveralls.io/github/open-contracting/lib-cove-ocds?branch=master
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/libcoveocds.svg
   :target: https://pypi.org/project/libcoveocds/


