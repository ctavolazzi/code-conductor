from setuptools import setup, find_packages
import os
import shutil

setup(
    name="ai_setup",
    version="0.4.0",
    description="AI-Setup toolkit for managing AI development environments and work efforts",
    author="AI-Setup Team",
    py_modules=["cli"],
    packages=find_packages(),
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "ai-setup=cli:main_entry",
            "ai-work-effort=work_efforts.scripts.ai_work_effort_creator:main",
        ],
    },
    install_requires=[
        "requests",
        "asyncio",
    ],
)