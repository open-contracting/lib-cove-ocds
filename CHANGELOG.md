# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## 0.11.2 (2023-02-23)

### Added

- Allow execution of command-line interface using `python -m libcoveocds`.

### Changed

- Drop support for Python 3.6 (end-of-life 2021-12-23).

### Fixed

- Add support for Bleach 6.

## 0.11.1 (2022-06-20)

### Fixed

- Extract the description of the `ocid` field in all languages.
- Label an extension as invalid if the extension metadata URL is empty or the release schema patch is not valid JSON.

## 0.11.0 (2021-05-20)

### Changed

- Check the combination of `ocid` and `id` is unique in releases, instead of just `id` https://github.com/open-contracting/cove-ocds/issues/127

## 0.10.2 (2021-05-13)

### Fixed

- Add a `record_pkg` keyword argument to the `ocds_json_output` function. Since 0.8.0 ([#44](https://github.com/open-contracting/lib-cove-ocds/pull/44)), the `ocds_json_output` function would check record packages against the release package schema.

## 0.10.1 (2021-04-10)

### Added

- Add Python wheels distribution.

## 0.10.0 (2021-02-25)

### Changed

- `common_checks_ocds` returns more fields on each error dictionary, so that we can [replace the message with a translation in cove-ocds](https://github.com/open-contracting/cove-ocds/pull/149)
- Update the default config to use branch urls instead of tag urls for the schema. This means patch fixes will automatically be pulled in.

### Fixed

- libcoveocds commandline fails for record packages https://github.com/open-contracting/lib-cove-ocds/issues/39

## 0.9.1 (2020-09-07)

### Fixed

- Fix package: Correct version number.

## 0.9.0 (2020-09-07)

### Added

- Add Unique IDs count to aggregates
- Added many options to CLI: convert, output-dir, schema-version, delete, exclude-file

### Changed

- Cache all requests in the tests https://github.com/OpenDataServices/lib-cove/pull/59

## 0.8.0 (2020-08-26)

### Changed

- Move OCDS specific code here from lib-cove https://github.com/open-contracting/lib-cove-ocds/pull/44

## 0.7.6 (2020-08-21)

- Upgrade to OCDS 1.1.5. Fix URL for codelists.

## 0.7.5 (2020-08-20)

- Upgrade to OCDS 1.1.5.

## 0.7.4 (2019-10-31)

### Fixed

- Needed dependencies were removed. 
Put back Python Dependencies until we can properly review which ones can be removed and which can't.
https://github.com/open-contracting/lib-cove-ocds/issues/31
- Don't error when looking up a path on a empty schema (e.g. due to broken refs)

## 0.7.3 (2019-09-23)

- Fix package: Indicate readme's encoding.

## 0.7.2 (2019-09-18)

- Fix package: Declare package dependencies.

## 0.7.1 (2019-08-21)

### Changed

- get_bad_ocds_prefixes no longer tests for hyphens after OCID prefixes, and no longer allows uppercase letters in OCID prefixes.

## 0.7.0 (2019-06-26)

### Changed

- OCDS Version 1.1.4 has been released! Changed default config to match
- The standard site is now available over SSL

## 0.6.1 (2019-06-14)

### Changed

- Load data in ordered to get consistent output

## 0.6.0 (2019-06-10)

### Changed

- Add handling of new additional fields context

## 0.5.1 (2019-05-31)

### Fixed

- When cache_all_requests was on, some requests were not being cached

## 0.5.0 (2019-05-09)

- Add additional check EmptyFieldCheck for records.

## 0.4.0 (2019-04-17)

### Added

- cache_all_requests config option, off by default.
- Add additional check EmptyFieldCheck for releases.

### Changed

- Upgraded lib-cove to v0.6.0
- The cache_schema option to SchemaOCDS and ocds_json_output is now deprecated; but for now it just sets the new cache_all_requests option


## 0.3.0 (2019-04-01)

### Changed

- Remove core code; use libcove instead.

### Fixed

- Record ocid now picked up when checking bad ocid prefix.
- Will not error if compiledRelease is not a object.  

## 0.2.2 (2018-11-14)

### Fixed

- get_file_type() - could not detect JSON file if extension was not "JSON" and filename had upper case letters in it

## 0.2.1 (2018-11-13)

### Fixed

- Corrected name of key broken in initial creation

## 0.2.0 (2018-11-13)

### Changed

- When duplicate ID's are detected, show a better message https://github.com/OpenDataServices/cove/issues/782
- Add config option for disable_local_refs mode in flatten-tool, default to on.
- Add config option for remove_empty_schema_columns mode in flatten-tool, default to on.

## 0.1.0 (2018-11-02)

### Added

- Added code for class: SchemaOCDS
- Added code for function: common_checks_ocds
- Added code for function: ocds_json_output
- Added CLI



