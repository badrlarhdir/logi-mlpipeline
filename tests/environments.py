from __future__ import annotations

import os
import pathlib
import shutil
from typing import Tuple

from click.testing import CliRunner

from mlpipeline.cli import cli
from mlpipeline.globals import PIPELINES_FOLDER

RESOURCES_FOLDER = "tests/resources"

# ---------------------------------------------------------------------------- #
#                       Functions used for the decorators                      #
# ---------------------------------------------------------------------------- #


def init_dvc_env(type, f_name: str | list[str]):
    """Initialize a simple example with the specified folder or file name

    Parameters
    ----------
    type : str
        The type of the file to delete, either "folder" or "file"
    f_name : str | list[str]
        The folder or file name
    """
    if type == "folder":
        # check if folder_name is a list
        if isinstance(f_name, list):
            for folder in f_name:
                init_dvc_env("folder", folder)
        else:
            if pathlib.Path(f_name).exists():
                shutil.rmtree(f_name)
            if pathlib.Path(f"{RESOURCES_FOLDER}/{f_name}").exists():
                shutil.copytree(f"{RESOURCES_FOLDER}/{f_name}", f"./{f_name}")

    if type == "file":
        if isinstance(f_name, list):
            for file in f_name:
                init_dvc_env("file", file)
        else:
            if pathlib.Path(f_name).exists():
                os.remove(f_name)
            if pathlib.Path(f"{RESOURCES_FOLDER}/{f_name}").exists():
                shutil.copy(f"{RESOURCES_FOLDER}/{f_name}", f"./{f_name}")


def delete_dvc_env(type, f_name: str | list[str]):
    """Deletes a file with the specified folder or file name

    Parameters
    ----------
    type : str
        The type of the file to delete, either "folder" or "file"
    f_name : str | list[str]
        The folder or file name
    """
    if type == "folder":
        # check if folder_name is a list
        if isinstance(f_name, list):
            for folder in f_name:
                delete_dvc_env("folder", folder)
        else:
            if pathlib.Path(f_name).exists():
                shutil.rmtree(f_name)

    if type == "file":
        if isinstance(f_name, list):
            for file in f_name:
                delete_dvc_env("file", file)
        else:
            if pathlib.Path(f_name).exists():
                os.remove(f_name)


def empty_environment():
    """Empty the environment from any previous test"""

    delete_dvc_env(
        "folder",
        [
            ".dvc",
            "notebooks",
            "data",
            "outputs",
            PIPELINES_FOLDER,
            ".github/workflows",
        ],
    )
    delete_dvc_env(
        "file",
        [
            "dvc.yaml",
            "params.yaml",
            ".dvcignore",
            "dvc.lock",
            "requirements.txt",
        ],
    )


def initialize_env(
    status: str,
    missing_folders: list[str] = [],
    missing_files: list[str] = [],
):
    """Clean the environment from any previous test"""

    init_env_folders = [".dvc", "notebooks", ".github/", "data", "outputs"]
    init_env_files = [
        "dvc.yaml",
        "params.yaml",
        ".dvcignore",
        "dvc.lock",
        "requirements.txt",
    ]

    # From the missing_folders and missing_files filter the init_env_folders and init_env_files lists
    init_env_folders = [
        folder for folder in init_env_folders if folder not in missing_folders
    ]
    init_env_files = [
        file for file in init_env_files if file not in missing_files
    ]

    if status == "start":
        init_dvc_env("folder", init_env_folders)
        init_dvc_env("file", init_env_files)

    if status == "end":
        delete_dvc_env("folder", init_env_folders)
        delete_dvc_env("file", init_env_files)

    if pathlib.Path(PIPELINES_FOLDER).exists():
        shutil.rmtree(PIPELINES_FOLDER)

    # remove any file that has as prefix the name of the pipeline in .github/workflows folder
    if pathlib.Path(".github/workflows").exists():
        for file in os.listdir(".github/workflows"):
            if file.endswith("-self-hosted-runner.yaml"):
                os.remove(f".github/workflows/{file}")


def initialize_data(data: list[str]):
    """Initialize the selected data from the resources data folder"""

    # Get data from the data folder
    for file in data:
        if pathlib.Path(f"{RESOURCES_FOLDER}/data/{file}").exists():
            shutil.copy(f"{RESOURCES_FOLDER}/data/{file}", f"data/{file}")


def initialize_notebooks():
    """Initialize the selected data from the resources data folder"""

    # copy the notebooks folder into notebooks folder
    if pathlib.Path(f"{RESOURCES_FOLDER}/notebooks").exists():
        shutil.copytree(
            f"{RESOURCES_FOLDER}/notebooks/",
            f"notebooks/",
            dirs_exist_ok=True,
        )


# ---------------------------------------------------------------------------- #
#                            Environment Decorators                            #
# ---------------------------------------------------------------------------- #


def emptyEnv(func):
    """Decorator to clean the environment from any previous test
    and to clean the environment after the test
    """

    def wrapper(*args, **kwargs):
        empty_environment()

        result = func(*args, **kwargs)

        empty_environment()
        return result

    return wrapper


def initializedEnv(func):
    """Decorator to clean the environment from any previous test
    and to clean the environment after the test
    """

    def wrapper(*args, **kwargs):
        initialize_env("start")

        result = func(*args, **kwargs)

        initialize_env("end")
        return result

    return wrapper


def notLinkedPipelineEnv(
    missing: dict,
    *pipelines: str,
):
    """Decorator to create a pipeline environment before the test
    and to clean the environment after the test

    Parameters
    ----------
    missing : dict
        The missing folders and files to dismiss from the initialization of the environment
    *pipelines : Tuple[str, ...]
        The names of the pipelines to create
    """

    missing_folders = missing["missing_folders"]
    missing_files = missing["missing_files"]

    def actual_decorator(func):
        def wrapper(*args, **kwargs):
            initialize_env("start", missing_folders, missing_files)

            runner = CliRunner()
            for pipeline in pipelines:
                result = runner.invoke(cli, ["create", "-p", pipeline])

            result = func(*args, **kwargs)

            initialize_env("end", missing_folders, missing_files)
            return result

        return wrapper

    return actual_decorator


def pipelineLinkedEnv(pipeline: str, notebooks: str, data: list[str]):
    """Decorator to create a pipeline environment linked to specified notebooks
    before the test and to clean the environment after the test

    Parameters
    ----------
    pipelines : str
        Name of the pipeline to create
    notebooks : str
        Names of the notebooks to link to the pipeline
    data :  list[str]
        List of Names of the data to link with the pipeline
    """

    def actual_decorator(func):
        def wrapper(*args, **kwargs):
            runner = CliRunner()

            # Initialize the environment
            result = runner.invoke(cli, ["init"])
            # Get data from the data folder
            initialize_data(data)
            # Get notebooks from the notebooks folder
            initialize_notebooks()

            # Copy requirements.txt from resources folder
            if pathlib.Path(f"{RESOURCES_FOLDER}/requirements.txt").exists():
                shutil.copy(
                    f"{RESOURCES_FOLDER}/requirements.txt", "requirements.txt"
                )

            # Create and link the pipeline
            result = runner.invoke(
                cli, ["create", "-p", pipeline, "-n", notebooks]
            )
            # Sync the pipeline
            result = runner.invoke(cli, ["sync", "-p", pipeline])

            result = func(*args, **kwargs)

            initialize_env("end")
            return result

        return wrapper

    return actual_decorator
