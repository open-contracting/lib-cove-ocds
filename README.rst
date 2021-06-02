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

Output JSON format
------------------

The output is an object with the following properties:

===================================== ===================== ==============
Property (key) name		      Type                  Value
===================================== ===================== ==============
``file_type``                         string                The type of the file supplied, e.g. ``json``
``version_used``                      string                The version of the OCDS schemas used, e.g. ``1.1``
``schema_url``                        string                The url to the package schema used, e.g. ``https://standard.open-contracting.org/1.1/en/release-package-schema.json``
``extensions``                        object                See extensions_
``validation_errors``                 array[object]         See validation_errors_
``common_error_types``                array[]               Always an empty array.
``deprecated_fields``                 array[object]         See deprecated_fields_
``releases_aggregates``               object                See releases_aggregates_
``records_aggregates``                object                See records_aggregates_
``additional_closed_codelist_values`` object                A mapping from from codelist path to an `additional codelist object`_.
``additional_open_codelist_values``   object                A mapping from from codelist path to an `additional codelist object`_.
``additional_checks``                 object                A mapping from additional check type (e.g. ``empty_field``) to a list of additional check objects, see below.
``conformance_errors``                object                See conformance_errors_
``additional_fields``                 array[object]         See additional_fields_
``all_additional_fields``             array[object]         See all_additional_fields_
``ocds_prefixes_bad_format``          array[]               This is a bug, and is always an empty array. See conformance_errors_ for where this property is actually populated.
===================================== ===================== ==============

_`extensions`
^^^^^^^^^^^^^

============================= ==================== ==============
Property (key) name	      Type                 Value
============================= ==================== ==============
``extensions``                array[object] 
``invalid_extensions``        array[array[string]]
``extended_schema_url``       string
``is_extended_schema``        boolean
============================= ==================== ==============

_`validation_errors`
^^^^^^^^^^^^^^^^^^^^

============================= ==================== ==============
Property (key) name	      Type                 Value
============================= ==================== ==============
``type``                      string
``field``                     string
``description``               string
``path``                      string
``value``                     any
============================= ==================== ==============

_`deprecated_fields`
^^^^^^^^^^^^^^^^^^^^

======================================= =========================== ==============
Property (key) name	                Type                        Value
======================================= =========================== ==============
``paths``                               array[string]
``explanation``                         array[string]               A 2 item array with deprecated version, and then an explanation.
``field``                               string
======================================= =========================== ==============

_`releases_aggregates`
^^^^^^^^^^^^^^^^^^^^^^

======================================= =========================== ==============
Property (key) name	                Type                        Value
======================================= =========================== ==============
``release_count``                       integer                     The number of items in the releases array 
``unique_ocids``                        array*                      A list of all ocids, deduplicated.
``unique_initation_type``               array*
``duplicate_release_ids``               array*
``tags``                                object
``unique_lang``                         array*
``unique_award_id``                     array*
``planning_count``                      integer
``tender_count``                        integer
``award_count``                         integer
``processes_award_count``               integer
``contract_count``                      integer
``processes_contract_count``            integer
``implementation_count``                integer
``processes_implementation_count``      integer
``min_release_date``                    string (date-time or "")
``max_release_date``                    string (date-time or "")
``min_tender_date``                     string (date-time or "")
``max_tender_date``                     string (date-time or "")
``min_award_date``                      string (date-time or "")
``max_award_date``                      string (date-time or "")
``min_contract_date``                   string (date-time or "")
``max_contract_date``                   string (date-time or "")
``unique_buyers_identifier``            object                      A mapping from identifier to name
``unique_buyers_name_no_id``            array*
``unique_suppliers_identifier``         object                      A mapping from identifier to name
``unique_suppliers_name_no_id``         array*
``unique_procuring_identifier``         object                      A mapping from identifier to name
``unique_procuring_name_no_id``         array*
``unique_tenderers_identifier``         object                      A mapping from identifier to name
``unique_tenderers_name_no_id``         array*
``unique_buyers``                       array[string]               A list of organisation names, with the identifier in brackets if it exists
``unique_suppliers``                    array[string]               A list of organisation names, with the identifier in brackets if it exists
``unique_procuring``                    array[string]               A list of organisation names, with the identifier in brackets if it exists
``unique_tenderers``                    array[string]               A list of organisation names, with the identifier in brackets if it exists
``unique_buyers_count``                 integer
``unique_suppliers_count``              integer
``unique_procuring_count``              integer
``unique_tenderers_count``              integer
``unique_org_identifier_count``         integer
``unique_org_name_count``               integer
``unique_org_count``                    integer
``unique_organisation_schemes``         array*
``organisations_with_address``          integer
``organisations_with_contact_point``    integer
``total_item_count``                    integer                     The sum of the following 3 item counts:
``tender_item_count``                   integer
``award_item_count``                    integer
``contract_item_count``                 integer
``unique_item_ids_count``               integer
``item_identifier_schemes``             array*
``unique_currency``                     array*
``planning_doc_count``                  integer
``tender_doc_count``                    integer
``tender_milestones_doc_count``         integer
``award_doc_count``                     integer
``contract_doc_count``                  integer
``implementation_doc_count``            integer
``implementation_milestones_doc_count`` integer
``planning_doctype``                    object                      A mapping from ``documentType``, to the number of occurrences.
``tender_doctype``                      object                      A mapping from ``documentType``, to the number of occurrences.
``tender_milestones_doctype``           object                      A mapping from ``documentType``, to the number of occurrences.
``award_doctype``                       object                      A mapping from ``documentType``, to the number of occurrences.
``contract_doctype``                    object                      A mapping from ``documentType``, to the number of occurrences.
``implementation_doctype``              object                      A mapping from ``documentType``, to the number of occurrences.
``implementation_milestones_doctype``   object                      A mapping from ``documentType``, to the number of occurrences.
``contracts_without_awards``            array                       An array of contract objects (from the data) that don't have awards.
======================================= =========================== ==============

_`records_aggregates`
^^^^^^^^^^^^^^^^^^^^^

============================= ==================== ==============
Property (key) name	      Type                 Value
============================= ==================== ==============
``count``                     integer              The number of items in the records array
``unique_ocids``              array*               A list of all ocids, deduplicated.
============================= ==================== ==============

_`additional codelist object`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

=========================== ===================== ==============
Property (key) name	    Type                  Value
=========================== ===================== ==============
``path``                    string
``field``                   string
``codelist``                string
``codelist_url``            string
``codelist_amend_urls``     array[array[string]]
``isopen``                  boolean
``values``                  array*
``extension_codelist``      boolean
=========================== ===================== ==============

_`additional check object`
^^^^^^^^^^^^^^^^^^^^^^^^^^

=========================== ===================== ==============
Property (key) name	    Type                  Value
=========================== ===================== ==============
``json_location``           string                e.g. ``releases/0/buyer``
=========================== ===================== ==============


_`conformance_errors`
^^^^^^^^^^^^^^^^^^^^^

============================= ============= ==============
Property (key) name	      Type          Value
============================= ============= ==============
``ocds_prefixes_bad_format``
``ocid_description``          string
``ocid_info_url``             string
============================= ============= ==============

_`additional_fields`
^^^^^^^^^^^^^^^^^^^^

============================= ==================== ==============
Property (key) name	      Type                 Value
============================= ==================== ==============
``path``                      string
``field``                     string
``usage_count``               integer
============================= ==================== ==============

_`all_additional_fields`
^^^^^^^^^^^^^^^^^^^^^^^^

=================================== ==================== ==============
Property (key) name	            Type                 Value
=================================== ==================== ==============
``count``                           integer
``examples``                        array*
``root_additional_field``           boolean
``additional_field_descendance``    object
``path``                            string
``field_name``                      string
=================================== ==================== ==============

array\*
^^^^^^^

An array marked with an asterisk is populated from fields in the data, so could be any type if the data doesn't conform to the schema.
