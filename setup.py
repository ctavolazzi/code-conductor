from setuptools import setup, find_packages
import os
import shutil

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="code-conductor",
    version="0.4.1",
    description="Code Conductor toolkit for managing AI development environments and work efforts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Code Conductor Team",
    author_email="ctavolazzi@gmail.com",  # Replace with your email
    url="https://github.com/ctavolazzi/code-conductor",
    py_modules=["cli"],
    packages=find_packages(),
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "code-conductor=cli:main_entry",
            "cc-worke=work_efforts.scripts.ai_work_effort_creator:main",
        ],
    },
    install_requires=[
        "requests",
        "asyncio",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    include_package_data=True,
)