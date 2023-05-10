import os

from click.testing import CliRunner

from mlpipeline.cli import cli

from .environments import (
    initializedEnv,
    notLinkedPipelineEnv,
    pipelineLinkedEnv,
)
from .globals import EXIT_CODE_SUCCESS

# ---------------------------------------------------------------------------- #
#                          Test on the run_local command                          #
# ---------------------------------------------------------------------------- #

# ----------------------------- Initialized Environment ---------------------------- #


@initializedEnv
def test_run_init_env():
    """Test the run command in an initialized environment"""

    runner = CliRunner()
    result = runner.invoke(cli, ["run_local"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert (
        "Please specify a pipeline name to run, set a default pipeline using the default command or use the --main or -m flag to run the main project"
        in result.output
    )


# ----------------------------- Pipeline Created ----------------------------- #


@pipelineLinkedEnv(
    "myfirstpipeline",
    "[notebooks/data_preprocess.ipynb, notebooks/train.ipynb, notebooks/upload_to_s3.ipynb]",
    ["train_data_cleaning.csv.dvc"],
)
def test_run_with_1_linked_pipeline():
    """Test the run command with a pipeline that does exist"""

    runner = CliRunner()

    result = runner.invoke(cli, ["run_local", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_SUCCESS

    assert "Running pipeline myfirstpipeline" in result.output
    assert "Pipeline myfirstpipeline ran successfully" in result.output


@notLinkedPipelineEnv(
    {
        "missing_folders": [],
        "missing_files": [],
    },
    "myfirstpipeline",
    "mysecondpipeline",
    "mythirdpipeline",
)
def test_run_with_3_pipelines():
    """Test the run pipeline command on a define pipeline in an environment with 3 pipelines"""

    runner = CliRunner()
    result = runner.invoke(cli, ["default", "-p", "mysecondpipeline"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline mysecondpipeline set as default" in result.output

    result = runner.invoke(cli, ["list"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "[Default] Pipeline: mysecondpipeline," in result.output

    result = runner.invoke(
        cli,
        [
            "link",
            "-p",
            "mysecondpipeline",
            "-n",
            "[notebooks/data_preprocess.ipynb, notebooks/train.ipynb]",
        ],
    )

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert (
        "Notebooks [notebooks/data_preprocess.ipynb, notebooks/train.ipynb] linked to pipeline mysecondpipeline"
        in result.output
    )

    result = runner.invoke(cli, ["run_local", "-p", "mysecondpipeline"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Running pipeline mysecondpipeline" in result.output
    assert "Pipeline mysecondpipeline ran successfully" in result.output
