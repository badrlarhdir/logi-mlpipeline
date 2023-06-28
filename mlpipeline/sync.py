from __future__ import annotations

import json
import os
import pathlib
import shutil

from .globals import PIPELINES_FOLDER
from .packagebuilder import setup_package
from .pipelinebuilder import pipeline_steps
from .reportbuilder import report_steps
from .utils import get_default_pipeline, get_notebooks_from_str


def sync_main_project(notebooks: list[str]):
    """Creates the required files for the dvc pipeline
    ----------
    notebooks:  list[str]
        list of the notebooks
    """

    pipeline_steps(notebooks)
    report_steps(notebooks)
    print("Main Project synced")


def sync_pipeline_project(notebooks: list[str], subfolder: str):
    """Copy the notebooks, requirements, data, dependencies, and gitignore files to the git repo
    Parameters
    ----------
    notebooks:  list[str]
        list of the notebooks
    """

    sync_main_project(notebooks)
    setup_package(notebooks, subfolder)


def sync_pipeline(pipeline: str):
    """Sync the notebooks of the selected pipeline
    Parameters
    ----------
    pipeline:  str
        name of the pipeline
    """

    print("Syncing pipeline", pipeline, "...")

    # Get the notebooks from the pipelines.json file
    pipelines_path = f"{PIPELINES_FOLDER}/pipelines.json"
    if pathlib.Path(pipelines_path).exists():
        with open(pipelines_path, "r") as pipelines_f:
            pipelines = json.load(pipelines_f)
            if pipeline not in pipelines:
                print("Pipeline not found")
                return
            if not pipelines[pipeline]:
                print("No notebooks found for this pipeline")
                return
            notebooks = get_notebooks_from_str(pipelines[pipeline])
            if not notebooks:
                print("No notebooks found for this pipeline")
                return
            # Package the pipeline project
            sync_pipeline_project(notebooks, pipeline)
    else:
        print("No pipelines found")
        return

    print(f"Pipeline {pipeline} synced")


def sync(
    notebooks: str | None,
    pipeline: str | None,
    force: bool | None,
    all: bool | None,
):
    """Sync the notebooks with the pipeline project or the main project

    Parameters
        (optional) notebooks (str | None): list of notebooks in the pipeline
        (optional) pipeline (str | None): name of the pipeline
        (optional) force (bool | None): forces creation of a new params.yaml file
        (optional) all (bool | None): sync all the pipelines (default: False)
    """

    # Sync all the pipelines
    if all:
        if force:
            # Iterate over all items in the folder
            for item in os.listdir(PIPELINES_FOLDER):
                item_path = os.path.join(PIPELINES_FOLDER, item)

                # Check if the item is a directory
                if os.path.isdir(item_path):
                    # Use shutil.rmtree to delete the directory and its contents
                    shutil.rmtree(item_path)

        # read the pipelines.json file and sync all the pipelines one by one
        pipelines_path = f"{PIPELINES_FOLDER}/pipelines.json"
        if pathlib.Path(pipelines_path).exists():
            with open(pipelines_path, "r") as pipelines_f:
                pipelines = json.load(pipelines_f)
                for pipeline in pipelines:
                    if pipeline != "default":
                        sync(None, pipeline, True, False)

                # Sync the default pipeline last to avoid overwriting the params.yaml file
                default_pipeline = get_default_pipeline()
                if default_pipeline:
                    sync(None, default_pipeline, True, False)
        return

    # remove the params.yaml file if force is True
    if force:
        # remove all the folders inside .github
        for folder in pathlib.Path(".github").iterdir():
            if folder.is_dir():
                shutil.rmtree(folder)

        pathlib.Path("params.yaml").unlink(missing_ok=True)
        pathlib.Path(f"{PIPELINES_FOLDER}/{pipeline}/params.yaml").unlink(
            missing_ok=True
        )

    if pipeline:
        sync_pipeline(pipeline)
        return
    if notebooks:
        print("Syncing notebooks on main project", notebooks, "...")
        list_notebooks = get_notebooks_from_str(notebooks)
        sync_main_project(list_notebooks)
        return

    # If no notebooks and no pipeline, sync the default pipeline
    if not notebooks and not pipeline:
        default_pipeline = get_default_pipeline()
        if default_pipeline:
            sync_pipeline(default_pipeline)
            return

    print("Please specify a pipeline name to sync or a list of notebooks")
