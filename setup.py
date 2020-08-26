from setuptools import find_packages, setup

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='libcoveocds',
    version='0.8.0',
    author='Open Data Services',
    author_email='data@open-contracting.org',
    url='https://github.com/open-contracting/lib-cove-ocds',
    description='A data review library for the Open Contracting Data Standard (OCDS)',
    license='AGPLv3',
    packages=find_packages(exclude=['tests', 'tests.*']),
    long_description=long_description,
    install_requires=[
        'libcove>=0.18.0',
        'bleach',
        'cached-property',
        'CommonMark',
        'Django',
        'json-merge-patch',
        'requests',
    ],
    extras_require={
        'test': [
            'coveralls',
            'pytest',
            'pytest-cov',
            'isort',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'libcoveocds = libcoveocds.cli.__main__:main',
        ],
    },
)
