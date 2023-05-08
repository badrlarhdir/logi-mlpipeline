from setuptools import find_packages, setup

setup(
    name="mlpipeline",
    version="0.0.1",
    description="ML Pipeline python package and CLI",
    author="Badr Larhdir",
    url="https://github.com/badrlarhdir/logi-mlpipeline",
    author_email="blarhdir@logitech.com",
    license="MIT",
    install_requires=[
        "pytest",
        "black",
        "blackdoc",
        "flake8",
        "mypy",
        "isort",
        "pathlib",
        "nbformat",
        "click",
        "pyyaml",
        "boto3",
        "requests",
        "tabulate"
    ],
    packages=find_packages(),
    entry_points={"console_scripts": "mlp = mlpipeline.cli:cli"},
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
    ],
)
