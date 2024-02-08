"""Packaging setup script."""

from setuptools import setup, find_packages

import pathlib

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text(encoding='utf-8')

VERSION = '0.0.1'

setup(
    name="gravy_tools",
    version=VERSION,
    author="podliva_2008 (Колесников Богдан)",
    author_email="mechanikbrother08@gmail.com",
    license="MIT",
    description='Инструменты для упрощения строительства на TeamCIS',
    long_description_content_type="text/markdown",
    long_description=README,
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=['pillow', 'requests'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Natural Language :: Russian"
    ]
)