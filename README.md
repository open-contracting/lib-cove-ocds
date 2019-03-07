# Lib Cove OCDS

## Command line

Call `libcoveocds` and pass the filename of some JSON data.

    libcoveocds tests/fixtures/common_checks/basic_1.json

## Code for use by external users

The only code that should be used directly by users is the `libcoveocds.config` and `libcoveocds.api` modules.

Other code ( Code in `libcore`, `lib`, etc) 
should not be used by external users of this library directly, as the structure and use of these may change more frequently.


## Updating dependencies

This is a bit messy; because we use two of our own packages and one of them isn't currently in pypi. Sorry.

  *  Update setup.py with any requirements this library needs, and update requirements.in if needed.
  *  Perform the usual steps to generate the txt files
  *  Go to the txt files and ...
        *  remove the line that starts "-e git+git@github.com:open-contracting/lib-cove-ocds.git". (This ends up here because of `-e .`, but we need that so the requirements in setup.py are installed.)
        *  remove the two error lines at the top that start "Skipping line in requirement file" and " (add #egg=PackageName to the URL to avoid this warning)"




