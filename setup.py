from setuptools import setup, find_packages

setup(
    name="resolution",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["data/*.json"],
    },
    install_requires=[
        "rich>=13.0",
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "resolution=resolution.cli:cli",
        ],
    },
    python_requires=">=3.8",
)

