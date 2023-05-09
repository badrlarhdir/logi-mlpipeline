import os

from .globals import PIPELINES_FOLDER


def show(
    pipeline: str,
):
    """Show the pipeline graph in the terminal"""

    # Run dvc dag in the correct path
    if pipeline:
        stream = os.popen(f"cd {PIPELINES_FOLDER}/{pipeline} && dvc dag")
    else:
        stream = os.popen("dvc dag")

    print(stream.read())
