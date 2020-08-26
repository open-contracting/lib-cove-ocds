# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2020-08-26

### Changed

- Move OCDS specific code here from lib-cove https://github.com/open-contracting/lib-cove-ocds/pull/44

## [0.7.6] - 2020-08-21

- Upgrade to OCDS 1.1.5. Fix URL for codelists.

## [0.7.5] - 2020-08-20

- Upgrade to OCDS 1.1.5.

## [0.7.4] - 2019-10-31

### Fixed

- Needed dependencies were removed. 
Put back Python Dependencies until we can properly review which ones can be removed and which cant.
https://github.com/open-contracting/lib-cove-ocds/issues/31
- Don't error when looking up a path on a empty schema (e.g. due to broken refs)

## [0.7.3] - 2019-09-23

- Fix package: Indicate readme's encoding in setup.py.

## [0.7.2] - 2019-09-18

- Fix package: Declare dependencies in setup.py.

## [0.7.1] - 2019-08-21

### Changed

- get_bad_ocds_prefixes no longer tests for hyphens after OCID prefixes, and no longer allows uppercase letters in OCID prefixes.

## [0.7.0] - 2019-06-26

### Changed

- OCDS Version 1.1.4 has been released! Changed default config to match
- The standard site is now available over SSL

## [0.6.1] - 2019-06-14

### Changed

- Load data in ordered to get consistant output

## [0.6.0] - 2019-06-10

### Changed

- Add handling of new additional fields context

## [0.5.1] - 2019-05-31

### Fixed

- When cache_all_requests was on, some requests were not being cached

## [0.5.0] - 2019-05-09

- Add additional check EmptyFieldCheck for records.

## [0.4.0] - 2019-04-17

### Added

- cache_all_requests config option, off by default.
- Add additional check EmptyFieldCheck for releases.

### Changed

- Upgraded lib-cove to v0.6.0
- The cache_schema option to SchemaOCDS and ocds_json_output is now deprecated; but for now it just sets the new cache_all_requests option


## [0.3.0] - 2019-04-01

### Changed

- Remove core code; use libcove instead.

### Fixed

- Record ocid now picked up when checking bad ocid prefix.
- Will not error if compiledRelease is not a object.  

## [0.2.2] - 2018-11-14

### Fixed

- get_file_type() - could not detect JSON file if extension was not "JSON" and filename had upper case letters in it

## [0.2.1] - 2018-11-13

### Fixed

- Corrected name of key broken in initial creation

## [0.2.0] - 2018-11-13

### Changed

- When duplicate ID's are detected, show a better message https://github.com/OpenDataServices/cove/issues/782
- Add config option for disable_local_refs mode in flatten-tool, default to on.
- Add config option for remove_empty_schema_columns mode in flatten-tool, default to on.

## [0.1.0] - 2018-11-02

### Added

- Added code for class: SchemaOCDS
- Added code for function: common_checks_ocds
- Added code for function: ocds_json_output
- Added CLI



