from setuptools import setup, find_packages

setup(
    name='libcoveocds',
    version='0.2.2',
    author='Open Data Services',
    author_email='code@opendataservices.coop',
    url='https://github.com/open-contracting/lib-cove-ocds',
    description='A data review library',
    packages=find_packages(),
    long_description='A data review library',
    install_requires=[
        'jsonref',
        'jsonschema',
        'CommonMark',
        'Django',
        'bleach',
        'requests',
        'json-merge-patch',
        'cached-property',
        # TODO Should also have flatten-tool >= v0.4.0 - that is currently in requirements instead.
    ],
    classifiers=[
            'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    ],
    entry_points='''[console_scripts]
libcoveocds = libcoveocds.cli.__main__:main''',
)
