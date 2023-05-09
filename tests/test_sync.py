import pathlib

from click.testing import CliRunner

from mlpipeline.cli import cli

from .environments import cleanEnv, pipelineEnv
from .globals import EXIT_CODE_CLICK_ERROR, EXIT_CODE_FAILED, EXIT_CODE_SUCCESS

# ---------------------------------------------------------------------------- #
#                           Test on the sync command                           #
# ---------------------------------------------------------------------------- #

# ----------------------------- Clean Environment ---------------------------- #


@cleanEnv
def test_sync_notebooks_missing_argument():
    """Test the sync command with a missing argument for the notebooks list"""

    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "-n"])

    assert result.exit_code == EXIT_CODE_CLICK_ERROR
    assert "Error: Option '-n' requires an argument." in result.output


@cleanEnv
def test_sync_notebooks_empty_argument():
    """Test the sync command with an empty argument for the notebooks list"""

    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "-n", ""])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert (
        "Please specify a pipeline name to sync or a list of notebooks"
        in result.output
    )


@cleanEnv
def test_sync_pipeline_missing_argument():
    """Test the sync command with a missing argument for the pipeline name"""

    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "-p"])

    assert result.exit_code == EXIT_CODE_CLICK_ERROR
    assert "Error: Option '-p' requires an argument." in result.output


@cleanEnv
def test_sync_pipeline_empty_argument():
    """Test the sync command with an empty argument for the pipeline name"""

    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "-p", ""])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert (
        "Please specify a pipeline name to sync or a list of notebooks"
        in result.output
    )


@cleanEnv
def test_sync_on_unexisting_notebooks():
    """Test the sync command with a list of notebooks that does not exist"""

    runner = CliRunner()
    result = runner.invoke(
        cli, ["sync", "-n", "[nbs/preprocessing.ipynb, nbs/training.ipynb]"]
    )

    assert result.exit_code == EXIT_CODE_FAILED

    assert not pathlib.Path("nbs").exists()
    assert not pathlib.Path("nbs/preprocessing.ipynb").exists()
    assert not pathlib.Path("nbs/training.ipynb").exists()


@cleanEnv
def test_sync_on_unexisting_pipeline():
    """Test the sync command with a pipeline that does not exist"""

    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "No pipelines found" in result.output


@cleanEnv
def test_sync_on_existing_notebooks():
    """Test the sync command with a list of notebooks that exist"""

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "sync",
            "-n",
            "[notebooks/data_preprocess.ipynb, notebooks/train.ipynb]",
        ],
    )

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline saved successfully" in result.output

    assert pathlib.Path("notebooks").exists()
    assert pathlib.Path("notebooks/data_preprocess.ipynb").exists()
    assert pathlib.Path("notebooks/train.ipynb").exists()


# ----------------------------- Pipeline Created ----------------------------- #


@pipelineEnv("myfirstpipeline")
def test_sync_on_created_pipeline_but_unlinked_notebooks():
    """Test the sync commands with a pipeline exists
    but with no linked notebooks
    """

    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "No notebooks found for this pipeline" in result.output
