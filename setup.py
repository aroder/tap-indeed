#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="tap-indeed",
    version="0.1.2",
    description="Singer.io tap for extracting job openings counts",
    author="dev@datateer.com",
    url="https://datateer.com",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_indeed"],
    install_requires=[
        "singer-python==5.9.0",
        "requests==2.23.0",
        "beautifulsoup4==4.9.0",
        "wheel"
    ],
    entry_points="""
    [console_scripts]
    tap-indeed=tap_indeed:main
    """,
    packages=find_packages(),
    package_data = {
        "schemas": ["tap_indeed/schemas/*.json"]
    },
    include_package_data=True,
)
