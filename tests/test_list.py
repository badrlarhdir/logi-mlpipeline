from click.testing import CliRunner

from mlpipeline.cli import cli

from .environments import initializedEnv, pipelineEnv
from .globals import EXIT_CODE_SUCCESS

# ---------------------------------------------------------------------------- #
#                           Test on the list command                           #
# ---------------------------------------------------------------------------- #

# ----------------------------- Initialized Environment ---------------------------- #


@initializedEnv
def test_list_init_env():
    """Test the list command in a initialized environment"""

    runner = CliRunner()
    result = runner.invoke(cli, ["list"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "No pipelines found" in result.output


# ----------------------------- Pipeline Created ----------------------------- #


@pipelineEnv(
    {
        "missing_folders": [],
        "missing_files": [],
    },
    "myfirstpipeline",
)
def test_list_with_1_existing_pipeline():
    """Test the sync commands with a pipeline that exists"""

    runner = CliRunner()
    result = runner.invoke(cli, ["list"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline: myfirstpipeline" in result.output


@pipelineEnv(
    {
        "missing_folders": [],
        "missing_files": [],
    },
    "myfirstpipeline",
    "mysecondpipeline",
    "mythirdpipeline",
)
def test_list_with_3_existing_pipeline():
    """Test the sync commands with three pipelines that exist"""

    runner = CliRunner()
    result = runner.invoke(cli, ["list"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline: myfirstpipeline" in result.output
    assert "Pipeline: mysecondpipeline" in result.output
    assert "Pipeline: mythirdpipeline" in result.output
