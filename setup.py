# -*- coding: utf-8 -*-
"""Installer for the imio.actionspanel package."""

from setuptools import find_packages
from setuptools import setup


long_description = open("README.rst").read() + "\n" + open("CHANGES.rst").read() + "\n"

setup(
    name="imio.actionspanel",
    version="2.0.0.dev0",
    description="Actions panel",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Addon",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    keywords="actions panel buttons",
    author="IMIO",
    author_email="dev@imio.be",
    url="https://github.com/imio/imio.actionspanel",
    download_url="https://pypi.org/project/imio.actionspanel",
    license="GPL",
    packages=find_packages("src", exclude=["ez_setup"]),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "Plone",
        "setuptools",
        "appy",
        "collective.fingerpointing",
        "imio.helpers>=1.3.0",
        "imio.history>=1.17",
        "plone.api",
    ],
    extras_require={
        "test": [
            "plone.app.robotframework",
            "plone.app.testing",
            "plone.testing",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
