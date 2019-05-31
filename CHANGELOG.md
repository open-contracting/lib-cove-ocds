# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.1] - 2019-05-31

### Fixed

- When cache_all_requests was on, some requests were not being cached

## [0.5.0] - 2019-05-09

### Added
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



