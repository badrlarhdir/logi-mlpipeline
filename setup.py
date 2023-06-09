from setuptools import find_packages, setup

setup(
    name="logi-mlpipeline",
    version="1.0.0",
    description="ML Pipeline python package and CLI",
    author="Badr Larhdir",
    url="https://github.com/badrlarhdir/logi-mlpipeline",
    author_email="blarhdir@logitech.com",
    license="MIT",
    package_data={
        "mlpipeline": [
            "resources/.gitignore",
            "resources/base.yaml",
            "resources/matrix_runner.yaml",
            "resources/single_runner.yaml",
            "resources/.gitignore.txt",
        ]
    },
    install_requires=[
        "pytest",
        "black",
        "blackdoc",
        "papermill",
        "flake8",
        "mypy",
        "ipykernel",
        "isort",
        "pathlib",
        "nbformat",
        "click",
        "pyyaml",
        "requests",
        "tabulate",
        "dvc[s3]",
    ],
    packages=find_packages(),
    entry_points={"console_scripts": "mlp = mlpipeline.cli:cli"},
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
    ],
)
