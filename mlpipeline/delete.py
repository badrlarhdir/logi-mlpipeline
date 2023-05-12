import json
import os
import pathlib
import shutil

from .globals import DEFAULT_PIPELINE, PIPELINES_FOLDER


def delete_pipeline(pipeline: str):
    """Delete the chosen pipeline folder and the GHA files
    Parameters
    ----------
    pipeline:  str
        name of the pipeline
    """

    # Remove the folder and its contents
    if not pathlib.Path(f"{PIPELINES_FOLDER}/{pipeline}").exists():
        print(f"Pipeline {pipeline} not found")
        return

    shutil.rmtree(f"{PIPELINES_FOLDER}/{pipeline}")

    # Remove all files starting with the name of the pipeline prefix insie the .github/workflows folder
    gha_path = ".github/workflows"
    prefix = pipeline
    if pathlib.Path(gha_path).exists():
        for file_name in os.listdir(gha_path):
            if file_name.startswith(prefix):
                file_path = os.path.join(gha_path, file_name)
                os.remove(file_path)

    # Update the pipelines.json file
    pipelines_path = f"{PIPELINES_FOLDER}/pipelines.json"
    if pathlib.Path(pipelines_path).exists():
        with open(pipelines_path, "r") as pipelines_f:
            pipelines = json.load(pipelines_f)
            if pipeline not in pipelines:
                print("Pipeline not found")
                return
            pipelines.pop(pipeline)
            if not pipelines:
                os.remove(pipelines_path)

        with open(pipelines_path, "w") as pipelines_f:
            json.dump(pipelines, pipelines_f)
    else:
        print(f"Pipeline {pipeline} not found")
        return

    print(f"Pipeline {pipeline} deleted")


def delete_all_pipelines():
    """Delete all the pipelines folders and the GHA files"""

    # For each pipeline in pipelines.json, delete the folder and the GHA files
    pipelines_path = f"{PIPELINES_FOLDER}/pipelines.json"
    if pathlib.Path(pipelines_path).exists():
        with open(pipelines_path, "r") as pipelines_f:
            pipelines = json.load(pipelines_f)
            for pipeline in pipelines:
                if pipeline != DEFAULT_PIPELINE:
                    delete_pipeline(pipeline)
        # delete the pipelines.json file
        os.remove(pipelines_path)
    else:
        print("No pipelines found")
        return

    # delete the params.yaml file even in notebooks if it exists
    params_path = "params.yaml"
    if pathlib.Path(params_path).exists():
        pathlib.Path(params_path).unlink()

    params_notebooks_path = "notebooks/params.yaml"
    if pathlib.Path(params_notebooks_path).exists():
        pathlib.Path(params_notebooks_path).unlink()

    print("All pipelines deleted")


def delete_default_pipeline(pipeline: str = None):
    """Delete the default pipeline folder and the GHA files

    Parameters
    ----------
    pipeline:  str
        name of the pipeline
    """

    # Set the default pipeline to an empty string if it is the one to be deleted
    # otherwise set the default pipeline to an empty string

    # verify that pipelines.json exists
    if not pathlib.Path(f"{PIPELINES_FOLDER}/pipelines.json").exists():
        return

    with open(f"{PIPELINES_FOLDER}/pipelines.json", "r") as pipelines_f:
        pipelines = json.load(pipelines_f)
        if (pipeline and pipelines[DEFAULT_PIPELINE] == pipeline) or (
            not pipeline
        ):
            pipelines[DEFAULT_PIPELINE] = ""
            with open(
                f"{PIPELINES_FOLDER}/pipelines.json", "w"
            ) as pipelines_f:
                json.dump(pipelines, pipelines_f)
            print(f"Default pipeline removed")


def delete(pipeline: str, all: bool):
    """Delete a pipeline or all the pipelines

    Parameters
        (optional) pipeline (str): name of the pipeline
        (optional) all (bool): remove all pipelines
    """

    if all:
        delete_all_pipelines()
        delete_default_pipeline()
        return
    if pipeline:
        delete_pipeline(pipeline)
        delete_default_pipeline(pipeline)
        return
    print(
        "Please specify a pipeline name using -p or use the --all or -a flag to delete all pipelines"
    )
