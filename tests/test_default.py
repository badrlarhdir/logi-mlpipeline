from click.testing import CliRunner

from mlpipeline.cli import cli

from .environments import initializedEnv, pipelineEnv
from .globals import EXIT_CODE_CLICK_ERROR, EXIT_CODE_SUCCESS

# ---------------------------------------------------------------------------- #
#                          Test on the default command                          #
# ---------------------------------------------------------------------------- #

# ----------------------------- Initialized Environment ---------------------------- #


@initializedEnv
def test_default():
    """Test the default command without any pipeline"""

    runner = CliRunner()
    result = runner.invoke(cli, ["default"])

    assert result.exit_code == EXIT_CODE_CLICK_ERROR
    assert "Error: Missing option '--pipeline' / '-p'." in result.output


@initializedEnv
def test_default_no_pipeline():
    """Test the default command when no pipeline exists"""

    runner = CliRunner()
    result = runner.invoke(cli, ["default", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline myfirstpipeline does not exist" in result.output


# ----------------------------- Pipeline Created ----------------------------- #


@pipelineEnv(
    {
        "missing_folders": [],
        "missing_files": [],
    },
    "myfirstpipeline",
)
def test_default_with_1_pipeline():
    """Test the create command with a pipeline that does exist"""

    runner = CliRunner()
    result = runner.invoke(cli, ["default", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline myfirstpipeline set as default" in result.output


@pipelineEnv(
    {
        "missing_folders": [],
        "missing_files": [],
    },
    "myfirstpipeline",
    "mysecondpipeline",
    "mythirdpipeline",
)
def test_default_with_3_pipelines():
    """Test the default pipeline command on a environment with 3 pipelines"""

    runner = CliRunner()
    result = runner.invoke(cli, ["default", "-p", "mysecondpipeline"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline mysecondpipeline set as default" in result.output

    result = runner.invoke(cli, ["list"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "[Default] Pipeline: mysecondpipeline," in result.output


@pipelineEnv(
    {
        "missing_folders": [],
        "missing_files": [],
    },
    "myfirstpipeline",
    "mysecondpipeline",
    "mythirdpipeline",
)
def test_default_with_3_pipelines_last_pipeline_default():
    """Test that the default pipeline is the last one initialized"""

    runner = CliRunner()
    result = runner.invoke(cli, ["list"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "[Default] Pipeline: mythirdpipeline," in result.output


@pipelineEnv(
    {
        "missing_folders": [],
        "missing_files": [],
    },
    "myfirstpipeline",
    "mysecondpipeline",
    "mythirdpipeline",
    "myfourthpipeline",
)
def test_default_with_4_pipelines_after_removing_last_created():
    """Test that the default is not always available in the list of pipelines"""

    runner = CliRunner()
    result = runner.invoke(cli, ["delete", "-p", "myfourthpipeline"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline myfourthpipeline deleted" in result.output

    result = runner.invoke(cli, ["list"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline: myfirstpipeline," in result.output
    assert "Pipeline: mysecondpipeline," in result.output
    assert "Pipeline: mythirdpipeline," in result.output
