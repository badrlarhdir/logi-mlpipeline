from __future__ import annotations

import os
import pathlib
import shutil
from typing import Tuple

from click.testing import CliRunner

from mlpipeline.cli import cli
from mlpipeline.globals import PIPELINES_FOLDER

RESOURCES_FOLDER = "tests/resources"


def init_dvc_env_folders(folder_name: str):
    """Initialize a simple example with the specified folder name

    Parameters
    ----------
    folder_name : str
        The folder name
    """
    # check if folder_name is a list
    if isinstance(folder_name, list):
        for folder in folder_name:
            init_dvc_env_folders(folder)
    else:
        if pathlib.Path(folder_name).exists():
            shutil.rmtree(folder_name)
        if pathlib.Path(f"{RESOURCES_FOLDER}/{folder_name}").exists():
            shutil.copytree(
                f"{RESOURCES_FOLDER}/{folder_name}", f"./{folder_name}"
            )


def init_dvc_env_files(file_name: str):
    """Initialize a simple example with the specified file name

    Parameters
    ----------
    file_name : str
        The file name
    """
    # check if file_name is a list
    if isinstance(file_name, list):
        for file in file_name:
            init_dvc_env_files(file)
    else:
        if pathlib.Path(file_name).exists():
            os.remove(file_name)
        if pathlib.Path(f"{RESOURCES_FOLDER}/{file_name}").exists():
            shutil.copy(f"{RESOURCES_FOLDER}/{file_name}", f"./{file_name}")


def delete_dvc_env_folders(folder_name: str):
    """Delete a file with the specified folder name

    Parameters
    ----------
    folder_name : str
        The folder name
    """
    # check if folder_name is a list
    if isinstance(folder_name, list):
        for folder in folder_name:
            delete_dvc_env_folders(folder)
    else:
        if pathlib.Path(folder_name).exists():
            shutil.rmtree(folder_name)


def delete_dvc_env_files(file_name: str):
    """Delete a file with the specified file name

    Parameters
    ----------
    file_name : str
        The file name
    """
    # check if file_name is a list
    if isinstance(file_name, list):
        for file in file_name:
            delete_dvc_env_files(file)
    else:
        if pathlib.Path(file_name).exists():
            os.remove(file_name)


def empty_environment():
    """Empty the environment from any previous test"""

    # No .github/workflows folder, no .dvc folder, no params.yaml, no dvc.yaml, no requirements.txt, no dvc.lock
    # no notebooks folder, no data folder, no outputs folder, no .dvcignore
    # no pipelines folder

    delete_dvc_env_folders(
        [
            ".dvc",
            "notebooks",
            "data",
            "outputs",
            PIPELINES_FOLDER,
            ".github/workflows",
        ]
    )
    delete_dvc_env_files(
        [
            "dvc.yaml",
            "params.yaml",
            ".dvcignore",
            "dvc.lock",
            "requirements.txt",
        ]
    )


def emptyEnv(func: callable):
    """Decorator to clean the environment from any previous test
    and to clean the environment after the test
    """

    def wrapper(*args, **kwargs):
        empty_environment()

        result = func(*args, **kwargs)

        empty_environment()
        return result

    return wrapper


def initialize_env(status: str):
    """Clean the environment from any previous test"""

    # Delete the pipelines folders if exists
    if status == "start":
        init_dvc_env_folders(
            [".dvc", "notebooks", ".github/", "data", "outputs"]
        )
        init_dvc_env_files(
            [
                "dvc.yaml",
                "params.yaml",
                ".dvcignore",
                "dvc.lock",
                "requirements.txt",
            ]
        )

    if status == "end":
        delete_dvc_env_folders(
            [".dvc", "notebooks", ".github/", "data", "outputs"]
        )
        delete_dvc_env_files(
            [
                "dvc.yaml",
                "params.yaml",
                ".dvcignore",
                "dvc.lock",
                "requirements.txt",
            ]
        )

    if pathlib.Path(PIPELINES_FOLDER).exists():
        shutil.rmtree(PIPELINES_FOLDER)

    # remove any file that has as prefix the name of the pipeline in .github/workflows folder
    if pathlib.Path(".github/workflows").exists():
        for file in os.listdir(".github/workflows"):
            if file.endswith("-self-hosted-runner.yaml"):
                os.remove(f".github/workflows/{file}")


def initializedEnv(func: callable):
    """Decorator to clean the environment from any previous test
    and to clean the environment after the test
    """

    def wrapper(*args, **kwargs):
        initialize_env("start")

        result = func(*args, **kwargs)

        initialize_env("end")
        return result

    return wrapper


def pipelineEnv(*pipelines: Tuple[str, ...]):
    """Decorator to create a pipeline environment before the test
    and to clean the environment after the test

    Parameters
    ----------
    *pipelines : Tuple[str, ...]
        The names of the pipelines to create
    """

    def actual_decorator(func: callable):
        def wrapper(*args, **kwargs):
            initialize_env("start")

            runner = CliRunner()
            for pipeline in pipelines:
                result = runner.invoke(cli, ["create", "-p", pipeline])

            result = func(*args, **kwargs)

            initialize_env("end")
            return result

        return wrapper

    return actual_decorator


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


def linkedPipelineEnv(pipeline: str, notebooks: str, data: list[str]):
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

    def actual_decorator(func: callable):
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
