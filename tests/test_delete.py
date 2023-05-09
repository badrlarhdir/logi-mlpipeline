import os

from click.testing import CliRunner

from mlpipeline.cli import cli

from .environments import cleanEnv, pipelineEnv
from .globals import EXIT_CODE_CLICK_ERROR, EXIT_CODE_FAILED, EXIT_CODE_SUCCESS

# ---------------------------------------------------------------------------- #
#                           Test on the delete command                           #
# ---------------------------------------------------------------------------- #

# ----------------------------- Clean Environment ---------------------------- #


@cleanEnv
def test_delete_uncreated_pipeline():
    """Test the delete command with a pipeline that does not exist"""

    runner = CliRunner()
    result = runner.invoke(cli, ["delete", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline myfirstpipeline not found" in result.output


@cleanEnv
def test_delete_all_uncreated_pipeline():
    """Test the delete --all/-a command with no pipeline that exists"""

    runner = CliRunner()
    result = runner.invoke(cli, ["delete", "-a"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "No pipelines found" in result.output


# ----------------------------- Pipeline Created ----------------------------- #


@pipelineEnv("myfirstpipeline")
def test_delete_created_pipeline():
    """Test the delete command with a pipeline that does not exist"""

    runner = CliRunner()
    result = runner.invoke(cli, ["delete", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline myfirstpipeline deleted" in result.output


@pipelineEnv("myfirstpipeline")
def test_delete_all_with_1_existing_pipeline():
    """Test the delete command with one pipeline that exists"""

    runner = CliRunner()
    result = runner.invoke(cli, ["delete", "-a"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline myfirstpipeline deleted" in result.output
    assert "All pipelines deleted" in result.output


@pipelineEnv("myfirstpipeline", "mysecondpipeline", "mythirdpipeline")
def test_delete_all_with_3_existing_pipelines():
    """Test the delete command with three pipelines that exist"""

    runner = CliRunner()
    result = runner.invoke(cli, ["delete", "-a"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline myfirstpipeline deleted" in result.output
    assert "Pipeline mysecondpipeline deleted" in result.output
    assert "Pipeline mythirdpipeline deleted" in result.output
    assert "All pipelines deleted" in result.output
