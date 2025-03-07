from setuptools import setup, find_packages

setup(
    name="ai_setup",
    version="0.2.1",
    description="AI-Setup toolkit for managing AI development environments and work efforts",
    author="AI-Setup Team",
    py_modules=["cli"],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "ai_setup=cli:main_entry",
        ],
    },
    install_requires=[
        "requests",
    ],
)