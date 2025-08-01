#!/usr/bin/env python3
"""
pdtab: Pandas-based Tabulation Library
=====================================

A comprehensive tabulation library for Python that replicates Stata's tabulate functionality
using pandas as the backend. This library provides one-way, two-way, and summary tabulations
with statistical tests and measures of association.

Author: pdtab Development Team
License: MIT
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    """Read README.md for long description."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "A comprehensive tabulation library for Python that replicates Stata's tabulate functionality."

# Read version from __init__.py
def read_version():
    """Read version from pdtab/__init__.py."""
    version_file = os.path.join(os.path.dirname(__file__), 'pdtab', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return "0.1.1"

setup(
    name="pdtab",
    version=read_version(),
    author="pdtab Development Team", 
    author_email="your.email@example.com",
    description="A pandas-based library that replicates Stata's tabulate functionality",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/pdtab/pdtab",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers", 
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0", 
        "scipy>=1.4.0",
        "matplotlib>=3.0.0",
        "seaborn>=0.11.0",
        "tabulate>=0.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "pre-commit>=2.0",
        ],
        "docs": [
            "sphinx>=3.0",
            "sphinx-rtd-theme>=0.5",
            "nbsphinx>=0.7",
            "jupyter>=1.0",
        ],
    },
    keywords="tabulation, crosstab, statistics, stata, pandas, data analysis",
    project_urls={
        "Bug Reports": "https://github.com/pdtab/pdtab/issues",
        "Source": "https://github.com/pdtab/pdtab",
        "Documentation": "https://pdtab.readthedocs.io/",
    },
    include_package_data=True,
    zip_safe=False,
)
