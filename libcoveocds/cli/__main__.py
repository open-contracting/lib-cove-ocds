import argparse
import json
import shutil
import tempfile

import libcoveocds.api


def main():
    parser = argparse.ArgumentParser(description='Lib Cove OCDS CLI')
    parser.add_argument("filename")

    args = parser.parse_args()

    cove_temp_folder = tempfile.mkdtemp(prefix='lib-cove-ocds-cli-', dir=tempfile.gettempdir())
    try:
        result = libcoveocds.api.ocds_json_output(
            cove_temp_folder,
            args.filename,
            None,
            convert=False,
            cache_schema=True,
            file_type='json'
        )
    finally:
        shutil.rmtree(cove_temp_folder)

    print(json.dumps(result, indent=4))


if __name__ == '__main__':
    main()
