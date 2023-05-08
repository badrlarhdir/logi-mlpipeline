from __future__ import annotations

import json
import pathlib

from .globals import DEFAULT_PIPELINE, PIPELINES_FOLDER


def get_notebooks_from_str(notebooks_str: str) -> list[str]:
    return list(filter(None, notebooks_str.replace("[", "").replace("]", "").replace(" ", "").split(",")))

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