import json
import pathlib

from .globals import PIPELINES_FOLDER


def link_notebooks_to_pipeline(notebooks: str, pipeline: str):
    ''' Link the notebooks to the selected pipeline
        Parameters
        ----------
        notebooks:  str
            list of the notebooks
        pipeline:  str
            name of the pipeline
    '''

    # Update the pipelines.json file
    pipelines_path = f"{PIPELINES_FOLDER}/pipelines.json"
    if pathlib.Path(pipelines_path).exists():
        with open(pipelines_path, 'r') as pipelines_f:
            pipelines = json.load(pipelines_f)
            pipelines[pipeline] = notebooks
        with open(pipelines_path, 'w') as pipelines_f:
            json.dump(pipelines, pipelines_f)
    else:
        print("No pipelines found")
        return

    print(f"Notebooks {notebooks} linked to pipeline {pipeline}")