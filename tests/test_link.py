from click.testing import CliRunner

from mlpipeline.cli import cli

from .environments import initEnv, pipelineEnv
from .globals import EXIT_CODE_CLICK_ERROR, EXIT_CODE_SUCCESS

# ---------------------------------------------------------------------------- #
#                          Test on the link command                          #
# ---------------------------------------------------------------------------- #

# ----------------------------- Initialized Environment ---------------------------- #


@initEnv
def test_link_missing_all_arguments():
    """Test the link command without any arguments"""

    runner = CliRunner()
    result = runner.invoke(cli, ["link"])

    assert result.exit_code == EXIT_CODE_CLICK_ERROR
    assert "Error: Missing option '--notebooks' / '-n'." in result.output


@initEnv
def test_link_uncreated_pipeline_with_notebooks_argument():
    """Test the link command with a list of notebooks but no pipeline created"""

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

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "No pipelines found" in result.output


# ----------------------------- Pipeline Created ----------------------------- #


@pipelineEnv("myfirstpipeline")
def test_link_pipeline_with_missing_notebooks_argument():
    """Test the link command with a create pipeline but no arguments"""

    runner = CliRunner()
    result = runner.invoke(cli, ["link", "-p", "myfirstpipeline"])

    assert result.exit_code == EXIT_CODE_CLICK_ERROR
    assert "Error: Missing option '--notebooks' / '-n'." in result.output


@pipelineEnv("myfirstpipeline")
def test_link_pipeline_with_notebooks_argument():
    """Test the link command with a create pipeline and a list of notebooks"""

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

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert (
        "Notebooks [notebooks/data_preprocess.ipynb, notebooks/train.ipynb] linked to pipeline myfirstpipeline"
        in result.output
    )
