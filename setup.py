#!/usr/bin/env python
"""
Heliodoro-repo setup script for building, installing, and distributing the package.
Supports entitlements, versioning, and automated deployment.
"""

from setuptools import setup, find_packages
import os

# Read version
version = os.environ.get("APP_VERSION", "0.1.0")

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="heliodoro",
    version=version,
    author="heliodorof44",
    author_email="user@example.com",
    description="Link sync merge build program integrated fill establish publish",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/heliodorof44/Heliodoro-repo",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "black>=22.0", "flake8>=4.0"],
        "docs": ["mkdocs>=1.5", "mkdocs-material>=9.5"],
    },
    entry_points={
        "console_scripts": [
            "heliodoro=heliodoro.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
