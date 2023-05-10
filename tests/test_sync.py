import pathlib

from click.testing import CliRunner

from mlpipeline.cli import cli

from .environments import (
    initializedEnv,
    notLinkedPipelineEnv,
    pipelineLinkedEnv,
)
from .globals import EXIT_CODE_CLICK_ERROR, EXIT_CODE_FAILED, EXIT_CODE_SUCCESS

# ---------------------------------------------------------------------------- #
#                           Test on the sync command                           #
# ---------------------------------------------------------------------------- #

# ----------------------------- Initialized Environment ---------------------------- #


@initializedEnv
def test_sync_notebooks_missing_argument():
    """Test the sync command with a missing argument for the notebooks list"""

    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "-n"])

    assert result.exit_code == EXIT_CODE_CLICK_ERROR
    assert "Error: Option '-n' requires an argument." in result.output


@initializedEnv
def test_sync_notebooks_empty_argument():
    """Test the sync command with an empty argument for the notebooks list"""

    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "-n", ""])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert (
        "Please specify a pipeline name to sync or a list of notebooks"
        in result.output
    )


@initializedEnv
def test_sync_pipeline_missing_argument():
    """Test the sync command with a missing argument for the pipeline name"""

    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "-p"])

    assert result.exit_code == EXIT_CODE_CLICK_ERROR
    assert "Error: Option '-p' requires an argument." in result.output


@initializedEnv
def test_sync_pipeline_empty_argument():
    """Test the sync command with an empty argument for the pipeline name"""

    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "-p", ""])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert (
        "Please specify a pipeline name to sync or a list of notebooks"
        in result.output
    )


@initializedEnv
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


@initializedEnv
def test_sync_on_unexisting_pipeline():
    """Test the sync command with a pipeline that does not exist"""

    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "No pipelines found" in result.output


@initializedEnv
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


@notLinkedPipelineEnv(
    {
        "missing_folders": [],
        "missing_files": [],
    },
    "myfirstpipeline",
)
def test_sync_on_created_pipeline_no_linked_notebooks():
    """Test the sync commands with an existing pipeline but no linked notebooks"""

    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "No notebooks found for this pipeline" in result.output


@pipelineLinkedEnv(
    "myfirstpipeline",
    "[notebooks/data_preprocess.ipynb, notebooks/train.ipynb, notebooks/upload_to_s3.ipynb]",
    ["train_data_cleaning.csv.dvc"],
)
def test_sync_on_created_pipeline_with_linked_notebooks():
    """Test the sync commands with an existing pipeline
    and with linked notebooks
    """

    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline saved successfully" in result.output


@notLinkedPipelineEnv(
    {
        "missing_folders": [".dvc"],
        "missing_files": [],
    },
    "myfirstpipeline",
)
def test_sync_on_created_pipeline_manually_linked_notebooks_with_missing_folder():
    """# Test the sync command with a list of linked notebooks that
    exist but with one missing folder"""

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "link",
            "-p",
            "myfirstpipeline",
            "-n",
            "[notebooks/data_preprocess.ipynb, notebooks/train.ipynb]",
        ],
    )
    result = runner.invoke(cli, ["sync", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_FAILED
    assert isinstance(result.exception, FileNotFoundError)
    assert (
        str(result.exception)
        == "[Errno 2] No such file or directory: './.dvc'"
    )


@notLinkedPipelineEnv(
    {
        "missing_folders": [".dvc", "notebooks"],
        "missing_files": [],
    },
    "myfirstpipeline",
)
def test_sync_on_created_pipeline_manually_linked_notebooks_with_missing_folders():
    """Test the sync command with a list of linked notebooks that
    exist but with missing folders"""

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "link",
            "-p",
            "myfirstpipeline",
            "-n",
            "[notebooks/data_preprocess.ipynb, notebooks/train.ipynb]",
        ],
    )
    result = runner.invoke(cli, ["sync", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_FAILED
    assert isinstance(result.exception, FileNotFoundError)
    # It will raise an error on the first missing file
    assert (
        str(result.exception)
        == "[Errno 2] No such file or directory: 'notebooks/data_preprocess.ipynb'"
    )


@notLinkedPipelineEnv(
    {
        "missing_folders": [],
        "missing_files": [".dvcignore"],
    },
    "myfirstpipeline",
)
def test_sync_on_created_pipeline_manually_linked_notebooks_with_missing_file():
    """Test the sync command with a list of linked notebooks that exist
    but with one missing file"""

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "link",
            "-p",
            "myfirstpipeline",
            "-n",
            "[notebooks/data_preprocess.ipynb, notebooks/train.ipynb]",
        ],
    )
    result = runner.invoke(cli, ["sync", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_FAILED
    assert isinstance(result.exception, Exception)
    assert (
        str(result.exception)
        == "[Errno 2] No such file or directory: './.dvcignore'"
    )


@notLinkedPipelineEnv(
    {
        "missing_folders": [],
        "missing_files": [".dvcignore", "requirements.txt"],
    },
    "myfirstpipeline",
)
def test_sync_on_created_pipeline_manually_linked_notebooks_with_missing_files():
    """Test the sync command with a list of linked notebooks that exist
    but with missing files"""

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "link",
            "-p",
            "myfirstpipeline",
            "-n",
            "[notebooks/data_preprocess.ipynb, notebooks/train.ipynb]",
        ],
    )
    result = runner.invoke(cli, ["sync", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_FAILED
    assert isinstance(result.exception, Exception)
    # It will raise an error on the first missing file
    assert (
        str(result.exception)
        == "No requirements.txt or setup_env folder found"
    )
