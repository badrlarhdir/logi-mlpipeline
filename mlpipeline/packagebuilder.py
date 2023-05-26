from __future__ import annotations

import os
import pathlib
import pdb
import shutil
import subprocess

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
        # if the setup_env folder or requirements.txt exists inside the subfolder delete it
        # first and then copy the new one
        if pathlib.Path(
            f"{PIPELINES_FOLDER}/{self.__subfolder}/setup_env"
        ).exists():
            shutil.rmtree(f"{PIPELINES_FOLDER}/{self.__subfolder}/setup_env")

        if pathlib.Path(
            f"{PIPELINES_FOLDER}/{self.__subfolder}/requirements.txt"
        ).exists():
            os.remove(
                f"{PIPELINES_FOLDER}/{self.__subfolder}/requirements.txt"
            )

        if pathlib.Path("./setup_env").exists():
            shutil.copytree(
                "./setup_env",
                f"{PIPELINES_FOLDER}/{self.__subfolder}/setup_env",
            )
        elif pathlib.Path("./requirements.txt").exists():
            shutil.copy(
                "requirements.txt",
                f"{PIPELINES_FOLDER}/{self.__subfolder}/requirements.txt",
            )
        else:
            raise Exception("No requirements.txt or setup_env folder found")

    def __copy_data_folder(self):
        """Copy the data folder to the git repo"""

        # Delete the data folder if it exists
        if pathlib.Path(
            f"{PIPELINES_FOLDER}/{self.__subfolder}/data"
        ).exists():
            shutil.rmtree(f"{PIPELINES_FOLDER}/{self.__subfolder}/data")

        # Run the git ls-files command and capture the output
        output = subprocess.check_output(
            [
                "git",
                "ls-files",
                "--exclude-standard",
                "--cached",
                "--others",
                "data",
            ]
        ).decode("utf-8")

        # Split the output into individual file paths
        file_paths = output.split("\n")

        # Remove any empty elements from the list
        file_paths = [path for path in file_paths if path]

        # Specify the destination folder where you want to copy the files
        destination_folder = f"{PIPELINES_FOLDER}/{self.__subfolder}"

        # Get the root path of the Git repository
        git_root = (
            subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
            .decode("utf-8")
            .strip()
        )

        # Copy each file to the destination folder
        for file_path in file_paths:
            # Construct the complete source file path
            source_file_path = os.path.join(git_root, file_path)

            # Construct the destination file path
            destination_file_path = os.path.join(destination_folder, file_path)

            # Create the destination folder if it doesn't exist
            os.makedirs(os.path.dirname(destination_file_path), exist_ok=True)

            # Copy the file to the destination folder
            shutil.copy(source_file_path, destination_file_path)

        # LEGACY: old code to copy the data folder to the git repo
        # shutil.copytree(
        #     "data",
        #     f"{PIPELINES_FOLDER}/{self.__subfolder}/data",
        #     dirs_exist_ok=True,
        # )

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

        # get the dependencies of the pipeline
        unique_deps = set(
            dep
            for stage in data["stages"]
            if "deps" in data["stages"][stage]
            for dep in data["stages"][stage]["deps"]
            if "data" not in dep
        )

        # get the outputs of the pipeline
        unique_outs = set(
            out
            for stage in data["stages"]
            if "outs" in data["stages"][stage]
            for out in data["stages"][stage]["outs"]
        )

        # remove the outputs from the dependencies
        unique_deps = unique_deps - unique_outs

        # TODO: clean this up for better readability
        for dep in unique_deps:
            # Check if the dependency is a file
            if os.path.isfile(dep) or os.path.isfile(f"./notebooks/{dep}"):
                # get the name of the dependency
                dep_name = dep.split("/")[-1]
                # get the url of the dependency
                split_url = dep.split("/")
                del split_url[-1]
                dep_url = "/".join(split_url)

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
                    # copy the dependency
                    shutil.copy(
                        dep,
                        os.getcwd()
                        + "/"
                        + f"{PIPELINES_FOLDER}/{self.__subfolder}/{dep_url}/{dep_name}",
                    )
            else:
                # if the dependency doesn't starts with .. it means that it is inside the notebooks folder
                if not dep.startswith(".."):
                    dep = f"./notebooks/{dep}"
                    # copy the folder to the pipeline folder
                    shutil.copytree(
                        dep,
                        os.getcwd()
                        + "/"
                        + f"{PIPELINES_FOLDER}/{self.__subfolder}/{dep}",
                        dirs_exist_ok=True,
                    )
                else:
                    # remove the first two dots
                    dep = dep[3:]
                    # copy the folder dependency
                    shutil.copytree(
                        dep,
                        os.getcwd()
                        + "/"
                        + f"{PIPELINES_FOLDER}/{self.__subfolder}/{dep}",
                        dirs_exist_ok=True,
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
