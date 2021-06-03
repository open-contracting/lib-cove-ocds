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
``additional_checks``                 object                A mapping from an additional check type (currently only ``empty_field``) to a list of `additional check objects <additional check object_>`_
``conformance_errors``                object                See conformance_errors_
``additional_fields``                 array[object]         Just the top level additional fields, see additional_fields_
``all_additional_fields``             array[object]         All additional fields, including children of other additional fields, see all_additional_fields_
``ocds_prefixes_bad_format``          array[]               This is a bug, and is always an empty array. See conformance_errors_ for where this property is actually populated.
===================================== ===================== ==============

Note that wherever a schema is used, it is the extended schema (if extensions exist).

extensions
^^^^^^^^^^

============================= ===================== ==============
Property (key) name	      Type                  Value
============================= ===================== ==============
``extensions``                array[object]         See `extensions/extensions`_
``invalid_extensions``        array[array[string]]  An array of pairs representing the extension url, and the error message, e.g. ``[["http://etc", "404: not found"]]``
``extended_schema_url``       string                The file the extended schema will be written to, if an output directory has been set, e.g. ``extended_schema.json``           
``is_extended_schema``        boolean               Has the schema been extended?
============================= ===================== ==============

extensions/extensions
^^^^^^^^^^^^^^^^^^^^^

======================= =============== ============
Property (key) name     Type            Value
======================= =============== ============
``url``                 string          The url of the extension's extension.json, e.g. ``https://raw.githubusercontent.com/open-contracting-extensions/ocds_metrics_extension/master/extension.json``
``schema_url``          string          The url of the extension's schema json e.g. ``https://raw.githubusercontent.com/open-contracting-extensions/ocds_metrics_extension/master/release-schema.json``
``description``         string          Taken from the extension.json
``name``                string          Taken from the extension.json
``documentationUrl``    string          Taken from the extension.json
``failed_codelists``    object          A mapping from extended codelist name (prefixed with ``+`` or ``-`` if appropriate) to human readable strings describing the error.
``codelists``           array[string]   Taken from the extension.json
======================= =============== ============

validation_errors
^^^^^^^^^^^^^^^^^

Note that this list will exclude codelists, which instead appear in ``additional_closed_codelist_values``.

======================= =========== ========
Property (key) name     Type        Value
======================= =========== ========
``type``                string      The JSON schema keyword that caused the validation error, e.g. ``minLength`` (`full list in the jsonschema lib <https://github.com/Julian/jsonschema/blob/9b6a9f5a4b7341cdbfc3cbee32d66bc190e4ced8/jsonschema/validators.py#L321-L345>`_), unless the schema keyword was ``type`` or ``format``, in which case this value is the relevant `type <https://datatracker.ietf.org/doc/html/draft-zyp-json-schema-04#section-3.5>`_ or `format <https://datatracker.ietf.org/doc/html/draft-fge-json-schema-validation-00#section-7.3>`_) e.g. ``array`` or ``date-time``
``field``               string      Like ``path``, but with array indices removed e.g. ``releases/tender/items``
``description``         string      A human readable message about the error, e.g. ``'id' is missing but required within 'items'``
``path``                string      The JSON Pointer to the erroneous data e.g. ``releases/0/tender/items/0``
``value``               any         The value in the data that was erroneous, or `""` if not applicable.
======================= =========== ========

deprecated_fields
^^^^^^^^^^^^^^^^^

======================================= =========================== ==============
Property (key) name	                Type                        Value
======================================= =========================== ==============
``paths``                               array[string]               JSON Pointers to the parent object with some deprecated data e.g. ``["releases/0/tender"]``
``explanation``                         array[string]               A 2 item array with deprecated version, and then an explanation., e.g. ``["1.1", "Some explanation text"]``
``field``                               string                      The field within the parent object that is deprecated, e.g. ``amendment``
======================================= =========================== ==============

releases_aggregates
^^^^^^^^^^^^^^^^^^^

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

records_aggregates
^^^^^^^^^^^^^^^^^^

============================= ==================== ==============
Property (key) name	      Type                 Value
============================= ==================== ==============
``count``                     integer              The number of items in the records array
``unique_ocids``              array*               A list of all ocids, deduplicated.
============================= ==================== ==============

additional codelist object
^^^^^^^^^^^^^^^^^^^^^^^^^^

=========================== ======================= ============
Property (key) name	    Type                    Value
=========================== ======================= ============
``path``                    string                  The path of the parent object, e.g. ``releases/tender/documents``
``field``                   string                  The JSON property name, e.g. ``documentType`` 
``codelist``                string                  The csv file containing the codelist, e.g. ``documentType.csv``
``codelist_url``            string                  A url that the codelist csv is accessible at, e.g. ``https://raw.githubusercontent.com/open-contracting/standard/1.1/schema/codelists/documentType.csv``
``codelist_amend_urls``     array[array[string]     urls of codelist csvs in extensions that amend the codelist. Structure is an array of pairs of ``+`` or ``-`` and the url. e.g. ``[["+", "https://raw.githubusercontent.com/open-contracting-extensions/ocds_tariffs_extension/d9df2969030b0a555c24c7db685262c714b4da24/codelists/+documentType.csv"]]``
``isopen``                  boolean                 Is this an open codelist?
``values``                  array*                  Values in the data that were not on the codelist
``extension_codelist``      boolean                 Was the codelist added by an extension? (Not just modified).
=========================== ======================= ============

additional check object
^^^^^^^^^^^^^^^^^^^^^^^

=========================== ===================== ==============
Property (key) name	    Type                  Value
=========================== ===================== ==============
``json_location``           string                A JSON Pointer to the data that was problematic e.g. ``releases/0/buyer``
=========================== ===================== ==============


conformance_errors
^^^^^^^^^^^^^^^^^^

=============================== ======================= =====
Property (key) name	        Type                    Value
=============================== ======================= =====
``ocds_prefixes_bad_format``    array[array[string]]    An array of pairs of the bad ocid value, and the JSON Pointer to it, e.g. ``["MY-ID", "releases/0/ocid"]``
``ocid_description``            string                  The descriptive text about ocids in the schema.
``ocid_info_url``               string                  The url to the information about identifiers in the reference docs
=============================== ======================= =====

additional_fields
^^^^^^^^^^^^^^^^^

============================= ========= ==============
Property (key) name	      Type      Value
============================= ========= ==============
``path``                      string    The path of the parent object, e.g. ``/publisher``
``field``                     string    The JSON property name, e.g. ``myField``
``usage_count``               integer   How many times this additional field appears
============================= ========= ==============

all_additional_fields
^^^^^^^^^^^^^^^^^^^^^

=================================== =========== ==============
Property (key) name	            Type        Value
=================================== =========== ==============
``count``                           integer     How many times this additional field appears
``examples``                        array*      An array of values for this field
``root_additional_field``           boolean     Is this the first additional field we find descending into this bit of the shcema? ie. is the parent in the schema?
``additional_field_descendance``    object      Only appears if ``root_additional_field`` is true. A mapping from paths, to objects like those in all_additional_fields_, for each of the additional fields that can be found by descending into the data from this field.
``path``                            string      The path of the parent object, e.g. ``/publisher``
``field_name``                      string      The JSON property name, e.g. ``myField``
=================================== =========== ==============

array\*
^^^^^^^

An array marked with an asterisk is populated from fields in the data, so could be any type if the data doesn't conform to the schema.
