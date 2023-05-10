import pathlib

from click.testing import CliRunner

from mlpipeline.cli import cli

from .environments import initializedEnv, notLinkedPipelineEnv
from .globals import EXIT_CODE_SUCCESS

# ---------------------------------------------------------------------------- #
#                          Test on the create command                          #
# ---------------------------------------------------------------------------- #

# ----------------------------- Initialized Environment ---------------------------- #


@initializedEnv
def test_create_new_pipeline():
    """Test the create command with a pipeline that does not exist"""

    runner = CliRunner()
    result = runner.invoke(cli, ["create", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline myfirstpipeline created" in result.output


@initializedEnv
def test_create_new_pipeline_with_notebook_links():
    """Test the create command with a pipeline that does not exist with notebook links"""

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "create",
            "-p",
            "myfirstpipeline",
            "-n",
            "[notebooks/data_preprocess.ipynb, notebooks/train.ipynb]",
        ],
    )

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline myfirstpipeline created" in result.output
    assert (
        "Notebooks [notebooks/data_preprocess.ipynb, notebooks/train.ipynb] linked to pipeline myfirstpipeline"
        in result.output
    )

    assert pathlib.Path("pipelines").exists()
    assert pathlib.Path("pipelines/myfirstpipeline").exists()
    assert pathlib.Path("pipelines/pipelines.json").exists()

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
def test_create_pipeline_that_already_exists():
    """Test the create command with a pipeline that does exist"""

    runner = CliRunner()
    result = runner.invoke(cli, ["create", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline myfirstpipeline already exists" in result.output
