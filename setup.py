from setuptools import setup, find_packages
import os
import shutil
import re

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the requirements.txt file
with open('requirements.txt') as f:
    required = f.read().splitlines()

# Get version from package __init__.py
with open('src/code_conductor/__init__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

setup(
    name="code-conductor",
    version=version,
    description="Code Conductor toolkit for managing AI development environments and work efforts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Code Conductor Team",
    author_email="ctavolazzi@gmail.com",  # Replace with your email
    url="https://github.com/ctavolazzi/code-conductor",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "code-conductor=code_conductor.cli.cli:main_entry",
            "cc-work-e=code_conductor.work_efforts.scripts.ai_work_effort_creator:main",
            "cc-index=code_conductor.scripts.index_work_efforts:main",
            "cc-new=code_conductor.scripts.cc_new:main",
            "cc-trace=code_conductor.scripts.cc_trace:main",
        ],
    },
    install_requires=required,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    include_package_data=True,
    package_data={
        '': ['templates/*.*', 'templates/**/*.*'],
    },
)