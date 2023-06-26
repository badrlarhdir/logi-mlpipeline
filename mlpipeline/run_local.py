import os
import subprocess

import yaml

from .default import get_default_pipeline
from .globals import PIPELINES_FOLDER
from .sync import sync_pipeline

RUN_PIPELINE_CMDS = ["dvc", "repro", "-f", "--no-commit", "--no-run-cache"]


def run_local(pipeline: str):
    """Run the dvc pipeline on the main project or on the selected pipeline

    Parameters
        (optional) pipeline (str): name of the pipeline
    """

    def find_all_dvc_files_and_pull_them():
        """Find all .dvc files in the project and pull them"""

        data_folder = "data"  # Specify the path to the data folder
        dvc_files = []

        # Find all .dvc files within the data folder
        for root, dirs, files in os.walk(data_folder):
            for file in files:
                if file.endswith(".dvc"):
                    dvc_files.append(os.path.join(root, file))

        # Process each .dvc file
        for dvc_file in dvc_files:
            # Read the contents of the .dvc file
            with open(dvc_file, "r") as file:
                dvc_content = yaml.safe_load(file)

                s3_path = dvc_content["deps"][0]["path"]

            outs_path = os.path.join(dvc_file.replace(".dvc", ""))

            print(
                "Pulling ",
                s3_path,
                " to ",
                outs_path,
            )

            # Call dvc import-url with the specific S3 path and output path
            subprocess.run(
                [
                    "dvc",
                    "import-url",
                    s3_path,
                    outs_path,
                ]
            )

    if pipeline == "main":
        print("Running main project...")
        find_all_dvc_files_and_pull_them()
        subprocess.run(RUN_PIPELINE_CMDS)

        # Reset dvc.lock file
        subprocess.run(["git", "reset", "--", "dvc.lock"])
        subprocess.run(["git", "checkout", "--", "dvc.lock"])

        print("Main project ran successfully")

        return

    # If no pipeline is specified, run the default pipeline
    if not pipeline:
        # Run the default pipeline
        pipeline = get_default_pipeline()

    # If a pipeline is specified OR if a default pipeline is found, run that pipeline
    if pipeline:
        print("Running pipeline", pipeline, "...")
        sync_pipeline(pipeline)

        # Change directory to the pipeline using os.chdir()
        os.chdir(os.path.join(PIPELINES_FOLDER, pipeline))
        find_all_dvc_files_and_pull_them()
        subprocess.run(RUN_PIPELINE_CMDS)

        path_pipeline_dvc_lock = f"./{PIPELINES_FOLDER}/{pipeline}/dvc.lock"

        print("Resetting dvc.lock file to the last commit...")
        # Reset dvc.lock file
        subprocess.run(["git", "reset", "--", path_pipeline_dvc_lock])
        subprocess.run(["git", "checkout", "--", path_pipeline_dvc_lock])

        print("Pipeline", pipeline, "ran successfully")

        return

    print(
        "Please specify a pipeline name to run, set a default pipeline using the default command or use the --main or -m flag to run the main project"
    )
