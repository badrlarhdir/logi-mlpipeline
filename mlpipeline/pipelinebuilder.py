from __future__ import annotations

import io
import pathlib
import shutil

import yaml
from nbformat import read

from .globals import PIPELINES_FOLDER


class PipelineBuilder:
    """Class to build the pipeline"""

    # Diagram of the process of building the pipeline files
    # set_notebooks -> clear_all_variables -> foreach notebook:
    # [add_deps_to_stage, add_outs_to_stage, link_params_to_stage, set_wdir_to_stage, set_pipeline_stage] -> save_pipeline

    def __init__(self):
        self.__dvc_stages = {}
        self.__params = {}

    def __clear_all_variables(self):
        """clear all variables for a new pipeline"""

        self.__dvc_stages = {}
        self.__params = {}

    """ dvc.yaml modifier """

    def __add_dvc_stage(self, stage: str):
        """Creates a key to the dvc stages

        Parameters
        ----------
        stage: str
            name of the stage
        """
        self.__dvc_stages[stage] = {"wdir": "notebooks"}

    def __check_dvc_stage(self, stage: str):
        """Checks if a key exists in the dvc stages

        Parameters
        ----------
        stage: str
            name of the stage
        """
        if stage not in self.__dvc_stages:
            self.__add_dvc_stage(stage)

    def __add_key_to_dvc_stage(self, stage: str, key: str, *args: tuple):
        """Add a key to the dvc stages

        Parameters
        ----------
        stage: str
            name of the stage
        """
        self.__check_dvc_stage(stage)
        self.__dvc_stages[stage][key] = list(args)

    def add_deps_to_stage(self, stage: str, *deps: tuple):
        """Add dependencies to the selected dvc stage

        Parameters
        ----------
        stage: str
            name of the stage
        *deps: tuple
            list of dependency names
        """
        self.__add_key_to_dvc_stage(stage, "deps", *deps)

    def add_outs_to_stage(self, stage: str, *outs: tuple):
        """Add outputs to the selected dvc stage

        Parameters
        ----------
        stage: str
            name of the stage
        *outs: tuple
            list of output names
        """
        self.__add_key_to_dvc_stage(stage, "outs", *outs)

    def link_params_to_stage(self, stage: str, *params: tuple):
        """Links params to the selected dvc stage

        Parameters
        ----------
        stage: str
            name of the stage
        *params: tuple
            list of parameter names
        """
        self.__add_key_to_dvc_stage(stage, "params", *params)

    def set_wdir_to_stage(self, stage: str, wdir: str):
        """Add a working directory to the selected dvc stage

        Parameters
        ----------
        stage: str
            name of the stage
        wdir: str
            name of the working directory
        """
        self.__check_dvc_stage(stage)
        self.__dvc_stages[stage]["wdir"] = wdir

    """ params.yaml modifier """

    def add_params_to_stage(self, stage: str, params: dict):
        """Add params to the selected stage

        Parameters
        ----------
        stage: str
            name of the stage
        params: dict
            dictionary of the keys available for papermill for a specific stage
        """
        self.__params[stage] = params

    """ pipeline constructor """

    def __add_cmd_to_stage(self, stage: str, cmd: str):
        """Add a command to the selected dvc stage

        Parameters
        ----------
        stage: str
            name of the stage
        cmd: str
            string of the command
        """
        self.__check_dvc_stage(stage)
        self.__dvc_stages[stage]["cmd"] = cmd

    def set_notebooks(self, notebooks: list[str], subfolder: str = None):
        """Add notebooks used in the pipeline

        Parameters
        ----------
        *notebooks: tuple
            name of the notebooks
        """
        self.__clear_all_variables()
        for notebook in notebooks:
            # Import the jupyter notebook
            if subfolder:
                notebook = f"{PIPELINES_FOLDER}/{subfolder}/{notebook}"

            try:
                with io.open(notebook, "r", encoding="utf-8") as f:
                    nb = read(f, 4)

                # Look for the pipeline methods inside the notebook's cells
                cells = list(
                    filter(lambda cell: "pipeline." in cell.source, nb.cells)
                )

                # Execute the pipeline methods
                for cell in cells:
                    exec(cell.source)
            except FileNotFoundError:
                print(f"File {notebook} not found!")
                raise

        # Save the pipeline to get the yaml files needed for DVC to run
        self.__save_pipeline(subfolder)

    def set_pipeline_stage(
        self, stage: str, notebook_name: str, output_name: str, params: dict
    ):
        """Build command for the specific stage (used for papermill & dvc)

        Parameters
        ----------
        stage: str
            name of the stage
        notebook_name: dict
            name of the working notebook
        notebook_path: dict
            name of the notebook path
        params: dict
            dictionary of the params used in the notebook
        """
        output_path = "../outputs/" + output_name
        notebook_path = "./" + notebook_name

        cmd_params = ""
        for key in params.keys():
            cmd_params += " -p" + " " + key + " " + "${" + params[key] + "} "

        cmd_params += " -k venv "

        cmd = f"papermill {notebook_path} {output_path} {cmd_params}"
        cmd = " ".join(cmd.split())

        self.__add_cmd_to_stage(stage, cmd)

    def __save_pipeline(self, subfolder: str = None):
        """Save the pipeline to their respective files"""

        def convert_dict_keys_to_list_recursive(dict_input):
            for key, value in dict_input.items():
                if isinstance(value, list):
                    if all(isinstance(item, list) for item in value):
                        for item in value:
                            convert_dict_keys_to_list_recursive({key: item})
                    else:
                        dict_input[key] = {"list": {key: value}}
                elif isinstance(value, dict):
                    dict_input[key] = convert_dict_keys_to_list_recursive(
                        value
                    )
                else:
                    continue
            return dict_input

        def save_dvc():
            dvc_yml = "dvc.yaml"

            if subfolder:
                dvc_yml = f"{PIPELINES_FOLDER}/{subfolder}/{dvc_yml}"

            # Save the dvc.yaml file in the root directory
            with open(dvc_yml, "w") as dvc_f:
                yaml.dump({"stages": self.__dvc_stages}, dvc_f)

        def save_params():
            params_yml = "params.yaml"
            wdir_params_yml = "notebooks/params.yaml"

            # Save the params.yaml file in the root directory
            # Main project params
            if not subfolder:
                # Check if the params.yaml file exists
                # if not, create it with the data from the pipeline
                if not pathlib.Path(params_yml).exists():
                    # Save the params.yaml file in the root directory
                    with open(params_yml, "w") as params_f:
                        yaml.dump(
                            convert_dict_keys_to_list_recursive(self.__params),
                            params_f,
                        )

                    # Save the params.yaml file in the working directory
                    with open(wdir_params_yml, "w") as wdir_params_f:
                        yaml.dump(
                            convert_dict_keys_to_list_recursive(self.__params),
                            wdir_params_f,
                        )
                # If params.yml has changed (i.e by a DS),
                # copy the old one in the working directory to sync both files
                else:
                    shutil.copyfile(params_yml, wdir_params_yml)

            # Pipeline params
            else:
                params_yml = f"{PIPELINES_FOLDER}/{subfolder}/{params_yml}"
                wdir_params_yml = (
                    f"{PIPELINES_FOLDER}/{subfolder}/{wdir_params_yml}"
                )

                # If the params.yaml doesn't exist,
                # copy the params.yaml from the root directory to the pipeline directory
                # then sync it with the one in the working directory
                if not pathlib.Path(params_yml).exists():
                    shutil.copyfile("params.yaml", params_yml)

                shutil.copyfile(params_yml, wdir_params_yml)

        save_dvc()
        save_params()

        print("Pipeline saved successfully")


pipeline = PipelineBuilder()


def pipeline_steps(notebooks: list[str], subfolder: str = None):
    pipeline.set_notebooks(notebooks, subfolder=subfolder)
