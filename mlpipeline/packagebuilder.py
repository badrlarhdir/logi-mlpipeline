from __future__ import annotations

import os
import pathlib
import shutil

import yaml

from .globals import PIPELINES_FOLDER
from .pipelinebuilder import pipeline_steps
from .reportbuilder import report_steps


class PackageBuilder:
    def __create_init_folder(self):
        """Create a folder named subfolder in the root directory"""

        c = str(os.getcwd() + f"/{PIPELINES_FOLDER}/{self.__subfolder}")
        os.makedirs(c, exist_ok=True)

    def __copy_requirements(self):
        """Copy the requirements.txt or the setup_env folder from the current directory to the directory
        of the git repository
        """
        if pathlib.Path("./setup_env").exists():
            if pathlib.Path(
                f"{PIPELINES_FOLDER}/{self.__subfolder}/setup_env"
            ).exists():
                shutil.rmtree(
                    f"{PIPELINES_FOLDER}/{self.__subfolder}/setup_env"
                )
            shutil.copytree(
                "./setup_env",
                f"{PIPELINES_FOLDER}/{self.__subfolder}/setup_env",
            )
        else:
            shutil.copy(
                "requirements.txt",
                f"{PIPELINES_FOLDER}/{self.__subfolder}/requirements.txt",
            )

    def __copy_data_folder(self):
        """Copy the data folder to the git repo"""

        shutil.copytree(
            "data",
            f"{PIPELINES_FOLDER}/{self.__subfolder}/data",
            dirs_exist_ok=True,
        )

    def __create_folder(self, folder_name: str):
        """Create a folder in the root directory

        Parameters
        ----------
        folder_name: tuple
            name of the folder you want to create
        """

        c = str(
            os.getcwd()
            + "/"
            + f"{PIPELINES_FOLDER}/{self.__subfolder}/{folder_name}"
        )
        os.makedirs(c, exist_ok=True)

    def __copy_dependencies(self):
        """Copy the dependencies of the pipeline to the git repository"""

        # Open the dvc.yaml file
        with open("dvc.yaml", "r") as dvc_f:
            data = yaml.safe_load(dvc_f)

        unique_deps = set()
        # Get the dependencies of the pipeline for each stage
        for stage in data["stages"]:
            for dep in data["stages"][stage]["deps"]:
                # get elements that are not from the data folder
                if "data" not in dep:
                    unique_deps.add(dep)

        for dep in unique_deps:
            # get the name of the dependency
            dep_name = dep.split("/")[-1]
            # get the url of the dependency
            split_url = dep.split("/")
            del split_url[-1]
            dep_url = "/".join(split_url)

            # TODO: Check if it is possible to have dependencies outside the notebooks folder

            # if the dependency doesn't starts with .. it means that it is inside the notebooks folder
            if not dep.startswith(".."):
                dep = f"./notebooks/{dep}"

                # create the folder
                os.makedirs(
                    os.getcwd()
                    + "/"
                    + f"{PIPELINES_FOLDER}/{self.__subfolder}/notebooks/{dep_url}",
                    exist_ok=True,
                )
                # copy the dependency
                shutil.copy(
                    dep,
                    os.getcwd()
                    + "/"
                    + f"{PIPELINES_FOLDER}/{self.__subfolder}/notebooks/{dep_url}/{dep_name}",
                )
            else:
                # remove the first two dots
                dep_url = dep_url[3:]
                dep = dep[3:]
                os.makedirs(
                    os.getcwd()
                    + "/"
                    + f"{PIPELINES_FOLDER}/{self.__subfolder}/{dep_url}",
                    exist_ok=True,
                )
                shutil.copy(
                    dep,
                    os.getcwd()
                    + "/"
                    + f"{PIPELINES_FOLDER}/{self.__subfolder}/{dep_url}/{dep_name}",
                )

            print("Copied dependency: " + dep)

    def __copy_gitignore(self):
        """Copy the .gitignore file from the current directory to
        the new repository
        """

        shutil.copy(
            os.path.join(os.path.dirname(__file__), "resources/.gitignore"),
            f"{PIPELINES_FOLDER}/{self.__subfolder}/.gitignore",
        )

    def copy_all(self, notebooks: list[str], subfolder: str = None):
        """Copy the notebooks, requirements, data, dependencies, and gitignore files
        to the git repo

        Parameters
        ----------
        *notebooks: tuple
            name of the notebooks
        """

        self.__subfolder = subfolder
        self.__create_init_folder()
        self.__create_folder("notebooks")
        self.__create_folder("outputs")
        self.__copy_requirements()
        self.__copy_data_folder()
        self.__copy_dependencies()
        self.__copy_gitignore()

        # Copy the notebooks of the pipeline
        for notebook in notebooks:
            print(notebook)
            # Copy the notebooks of the pipeline
            shutil.copy(
                notebook, f"{PIPELINES_FOLDER}/{self.__subfolder}/notebooks"
            )
            print("Copied notebook: " + notebook)


package = PackageBuilder()


def setup_package(notebooks: list[str], subfolder: str):
    """Copy the notebooks, requirements, data, dependencies, and gitignore files
    to the git repo
    Parameters
    ----------
    *notebooks: tuple
        name of the notebooks
    subfolder: str
        name of the subfolder where the pipeline are located
    """

    package.copy_all(notebooks, subfolder)
    pipeline_steps(notebooks, subfolder)
    report_steps(notebooks, subfolder)
