from __future__ import annotations

import io
import os
import pathlib
import shutil

import yaml
from nbformat import read

from .globals import PIPELINES_FOLDER

DEFAULT_CMDS = "# Reproduce pipeline if any changes detected in dependencies\ndvc pull --allow-missing\ndvc repro -f\n# Output experiment results\ndvc exp show\n\n# Output the hash commit into the report\ngit log --pretty=format:'%h' -n 1 >> report.md\n\n"


class ReportBuilder:
    """Class to build the report.md file"""

    # Diagram of the process of building the report.md file
    # set_notebooks -> clear_all_variables -> foreach notebook: [add_text_to_report, add_comment_to_report, add_img_to_report] -> save_report

    def __init__(self):
        self.__report_cmds = DEFAULT_CMDS

    def __clear_all_variables(self):
        self.__report_cmds = DEFAULT_CMDS

    def add_text_to_report(self, text: str):
        """Add text to the report.md

        Parameters
        ----------
        text: str
        """

        self.__report_cmds += f"echo '{text}' >> report.md\n"

    def add_comment_to_report(self, text: str):
        """Add comment to the report.md

        Parameters
        ----------
        text: str
        """

        self.__report_cmds += f"{text}\n"

    def add_img_to_report(self, img_link: str, alias: str = ""):
        """Add an image to the report.md

        Parameters
        ----------
        img_link: str
            reference of the image
        alias: str
            alias for the image
        """

        self.__report_cmds += f"echo '![{alias}]({img_link})' >> report.md\n"

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
            with io.open(notebook, "r", encoding="utf-8") as f:
                nb = read(f, 4)

            # Look for the report methods inside the notebook's cells
            cells = list(
                filter(lambda cell: "report." in cell.source, nb.cells)
            )

            # Execute the report methods
            for cell in cells:
                exec(cell.source)

        # Save the report to get the yaml file needed for github action job
        self.__save_report(subfolder)

    def __save_report(self, subfolder: str = None):
        """Save the cml report"""

        with open(
            os.path.join(os.path.dirname(__file__), "resources/base.yaml"), "r"
        ) as base_f:
            data_self_hosted_runner = yaml.safe_load(base_f)

        # Add the report commands to the GHA job for the self hosted runner
        self.__report_cmds += "cml comment create report.md\n"
        data_self_hosted_runner["on"] = {
            "repository_dispatch": {
                "types": [
                    "mlpipeline-main"
                    if not subfolder
                    else f"mlpipeline-{subfolder}"
                ],
            }
        }
        data_self_hosted_runner["jobs"]["pipeline"]["steps"][-1][
            "run"
        ] = self.__report_cmds

        # Find the index of the step "Install requirements"
        # and add the setup_env command if it exists
        # otherwise add an install requirements step
        for step in data_self_hosted_runner["jobs"]["pipeline"]["steps"]:
            if step.get("name") == "Install requirements":
                index_requirements = data_self_hosted_runner["jobs"][
                    "pipeline"
                ]["steps"].index(step)

                data_self_hosted_runner["jobs"]["pipeline"]["steps"][
                    index_requirements
                ]["run"] = (
                    "pip install -r requirements.txt\n"
                    if not pathlib.Path("./setup_env").exists()
                    else "source setup_env/setup_env.sh\n"
                )

                # Add the command to make papermill work on the created virtualenv
                data_self_hosted_runner["jobs"]["pipeline"]["steps"][
                    index_requirements
                ][
                    "run"
                ] += "\n#to make papermill work on the created virtualenv\npython -m ipykernel install --user --name venv --display-name 'venv'\n"

                break

        # Setup the Pipeline folder
        if subfolder:
            # Copy the .dvc folder from the main repo to the pipeline folder
            # verify that the .dvc folder exists

            # Copy the .dvc folder to the pipeline folder
            if pathlib.Path(f"{PIPELINES_FOLDER}/{subfolder}/.dvc").exists():
                shutil.rmtree(f"{PIPELINES_FOLDER}/{subfolder}/.dvc")
            shutil.copytree("./.dvc", f"{PIPELINES_FOLDER}/{subfolder}/.dvc")

            # Copy the outputs folder to the pipeline folder
            if pathlib.Path(
                f"{PIPELINES_FOLDER}/{subfolder}/outputs"
            ).exists():
                shutil.rmtree(f"{PIPELINES_FOLDER}/{subfolder}/outputs")
            shutil.copytree(
                "./outputs", f"{PIPELINES_FOLDER}/{subfolder}/outputs"
            )

            # Copy the dvc.lock file to the pipeline folder
            if pathlib.Path("./dvc.lock").exists():
                shutil.copy(
                    "./dvc.lock", f"{PIPELINES_FOLDER}/{subfolder}/dvc.lock"
                )
            # Copy the .dvcignore file to the pipeline folder
            shutil.copy(
                "./.dvcignore", f"{PIPELINES_FOLDER}/{subfolder}/.dvcignore"
            )

            # Set the name of the GHA jobs
            data_self_hosted_runner[
                "name"
            ] = f"{subfolder} Self Hosted Runner ML-pipeline"

            # Set the working directory for the self hosted runner to
            # the pipeline folder
            data_self_hosted_runner["jobs"]["pipeline"]["defaults"] = {
                "run": {"working-directory": f"{PIPELINES_FOLDER}/{subfolder}"}
            }

        # Make the .github/workflows directory if it doesn't exist
        gh_workflows_path = pathlib.Path("./.github/workflows")
        if subfolder:
            gh_workflows_path = pathlib.Path(
                f"./{PIPELINES_FOLDER}/{subfolder}/.github/workflows"
            )
        pathlib.Path(gh_workflows_path).mkdir(parents=True, exist_ok=True)

        # Create the job (.yaml) files for both self hosted runner & github hosted runner

        # If the subfolder doesn't exist, it means that the report is for the main repo,
        # otherwise for a pipeline
        if not subfolder:
            # Copy the self-hosted-runner.yaml to the main repo
            with open(
                gh_workflows_path / "self-hosted-runner.yaml", "w"
            ) as self_hosted_runner_f:
                yaml.dump(
                    data_self_hosted_runner,
                    self_hosted_runner_f,
                    sort_keys=False,
                )
        else:
            # Copy the self-hosted-runner.yamlto the subfolder repo
            with open(
                gh_workflows_path / f"{subfolder}-self-hosted-runner.yaml", "w"
            ) as self_hosted_runner_f:
                yaml.dump(
                    data_self_hosted_runner,
                    self_hosted_runner_f,
                    sort_keys=False,
                )
            # Copy the file to the main repo too
            with open(
                f"./.github/workflows/{subfolder}-self-hosted-runner.yaml", "w"
            ) as self_hosted_runner_f:
                yaml.dump(
                    data_self_hosted_runner,
                    self_hosted_runner_f,
                    sort_keys=False,
                )

        print("Report saved successfully")


report = ReportBuilder()


def report_steps(notebooks: list[str], subfolder: str = None):
    report.set_notebooks(notebooks, subfolder=subfolder)
