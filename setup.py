from setuptools import find_packages, setup

with open("README.rst") as f:
    long_description = f.read()

setup(
    name="libcoveocds",
    version="0.10.2",
    author="Open Data Services",
    author_email="data@open-contracting.org",
    url="https://github.com/open-contracting/lib-cove-ocds",
    description="A data review library for the Open Contracting Data Standard (OCDS)",
    license="AGPLv3",
    packages=find_packages(exclude=["tests", "tests.*"]),
    long_description=long_description,
    long_description_content_type="text/x-rst",
    install_requires=[
        "libcove>=0.22.0",
        "bleach",
        "django",
        "json-merge-patch",
        "jsonschema",
        "markdown-it-py",
        "requests",
        "click",
    ],
    extras_require={
        "test": [
            "coveralls",
            "pytest",
            "pytest-cov",
            "isort",
        ],
    },
    classifiers=[
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={
        "console_scripts": [
            "libcoveocds = libcoveocds.cli.__main__:process",
        ],
    },
)
