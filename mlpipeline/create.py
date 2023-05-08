import os
import pathlib
import json

from mlpipeline.globals import PIPELINES_FOLDER, DEFAULT_PIPELINE

from .link import link_notebooks_to_pipeline

def create_pipeline(pipeline: str):
    ''' Create a pipeline project folder inside the pipelines folder
        Parameters
        ----------
        pipeline:  str
            name of the pipeline
    '''

    if pipeline == "main":
        print("Pipeline name cannot be main")
        return

    # Create the directory if it does not exist
    if pathlib.Path(os.path.join(PIPELINES_FOLDER, pipeline)).exists():
        print(f"Pipeline {pipeline} already exists")
        return
    
    os.makedirs(os.path.join(PIPELINES_FOLDER, pipeline))
    
    pipelines_path = f"{PIPELINES_FOLDER}/pipelines.json"
    # Create the params.yaml file with the pipeline name as key and empty string as value
    # and set the pipeline to the default one in the pipelines.json file
    if pathlib.Path(pipelines_path).exists():
        with open(pipelines_path, 'r') as pipelines_f:
            pipelines = json.load(pipelines_f)

        pipelines[pipeline] = ''
        pipelines[DEFAULT_PIPELINE] = pipeline
    else:
        pipelines = {pipeline: '', DEFAULT_PIPELINE: pipeline}
        
    with open(pipelines_path, 'w') as pipelines_f:
        json.dump(pipelines, pipelines_f)

    print(f"Pipeline {pipeline} created")

def create(pipeline: str, notebooks: str):
    '''Create a pipeline project

    Parameters
        (optional) notebooks (str): list of notebooks in the pipeline
        pipeline (str): name of the pipeline
    '''

    create_pipeline(pipeline)
    if notebooks:
        link_notebooks_to_pipeline(notebooks, pipeline)