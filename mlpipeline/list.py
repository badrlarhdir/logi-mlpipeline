import json
import pathlib

from .globals import DEFAULT_PIPELINE, PIPELINES_FOLDER


def list_pipelines():
    """List the pipelines"""

    pipelines_path = f"{PIPELINES_FOLDER}/pipelines.json"
    if pathlib.Path(pipelines_path).exists():
        with open(pipelines_path, "r") as pipelines_f:
            pipelines = json.load(pipelines_f)
            for pipeline in pipelines:
                if pipeline != DEFAULT_PIPELINE:
                    print(
                        f"{'[Default] ' if pipelines[DEFAULT_PIPELINE] == pipeline else ''}Pipeline: {pipeline}, notebooks: {pipelines[pipeline]}"
                    )
    else:
        print("No pipelines found")
