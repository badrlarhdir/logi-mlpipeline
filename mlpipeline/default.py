import pathlib
import json

from mlpipeline.globals import PIPELINES_FOLDER, DEFAULT_PIPELINE

def set_default_pipeline(pipeline: str):
    ''' Set the default pipeline to be used when no pipeline is specified

    Parameters
        (optional) pipeline (str): name of the pipeline
    '''

    # Check if the pipeline exists
    # If it does, set it as the default pipeline
    pipelines_path = f"{PIPELINES_FOLDER}/pipelines.json"
    if pathlib.Path(pipelines_path).exists():
        with open(pipelines_path, 'r') as pipelines_f:
            pipelines = json.load(pipelines_f)
            if pipeline in pipelines:
                pipelines[DEFAULT_PIPELINE] = pipeline
                with open(pipelines_path, 'w') as pipelines_f:
                    json.dump(pipelines, pipelines_f)
                print(f"Pipeline {pipeline} set as default")
                return
    print(f"Pipeline {pipeline} does not exist")

def get_default_pipeline():
    # Check if the default pipeline exists in the pipelines.json file
    pipelines_path = f"{PIPELINES_FOLDER}/pipelines.json"
    if pathlib.Path(pipelines_path).exists():
        with open(pipelines_path, 'r') as pipelines_f:
            pipelines = json.load(pipelines_f)
            if DEFAULT_PIPELINE not in pipelines:
                print(f"Default pipeline not found")
                return None
            else:
                if len(pipelines[DEFAULT_PIPELINE]) == 0:
                    print(f"No default pipeline set")
                    return None
            return pipelines[DEFAULT_PIPELINE]