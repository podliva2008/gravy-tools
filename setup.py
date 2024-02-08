from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'Инструменты для упрощения строительства на TeamCIS'
LONG_DESCRIPTION = 'Инструменты для упрощения строительства на TeamCIS засчёт удобного интерфейса, скриптов и редактора мира на локальном сервере'

# Setting up
setup(
    name="gravy-tools",
    version=VERSION,
    author="podliva_2008 (Колесников Богдан)",
    author_email="<mechanikbrother08@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['pillow', 'requests'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Natural Language :: Russian"
    ]
)