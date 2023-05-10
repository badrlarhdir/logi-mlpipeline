import pathlib

from click.testing import CliRunner

from mlpipeline.cli import cli

from .environments import emptyEnv, initializedEnv, linkedPipelineEnv
from .globals import EXIT_CODE_SUCCESS

# ---------------------------------------------------------------------------- #
#                          Test on the show command                          #
# ---------------------------------------------------------------------------- #

# ----------------------------- Empty Environment ---------------------------- #


@emptyEnv
def test_show_on_empty_env():
    """Test the show command in an empty environment"""

    runner = CliRunner()
    result = runner.invoke(cli, ["show"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "" in result.output


# ----------------------------- Initialized Environment ---------------------------- #


@initializedEnv
def test_show_on_already_init_env():
    """Test the show command in an environment that was already initialized"""

    runner = CliRunner()
    result = runner.invoke(cli, ["show"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "" in result.output


# ----------------------------- Pipeline Created ----------------------------- #


@linkedPipelineEnv(
    "myfirstpipeline",
    "[notebooks/data_preprocess.ipynb, notebooks/train.ipynb]",
    ["train_data_cleaning.csv.dvc"],
)
def test_show_with_1_linked_pipeline_and_2_notebooks():
    """Test the show command with a pipeline that does exist"""

    runner = CliRunner()
    result = runner.invoke(cli, ["show"])

    assert result.exit_code == EXIT_CODE_SUCCESS

    assert "data/train_data_cleaning.csv" in result.output
    assert "data_preprocess" in result.output
    assert "train" in result.output
    assert not "upload_to_s3" in result.output


@linkedPipelineEnv(
    "myfirstpipeline",
    "[notebooks/data_preprocess.ipynb, notebooks/train.ipynb, notebooks/upload_to_s3.ipynb]",
    ["train_data_cleaning.csv.dvc"],
)
def test_show_with_1_linked_pipeline_and_3_notebooks():
    """Test the show command with a pipeline that does exist"""

    runner = CliRunner()
    result = runner.invoke(cli, ["show"])

    assert result.exit_code == EXIT_CODE_SUCCESS

    assert "data/train_data_cleaning.csv" in result.output
    assert "data_preprocess" in result.output
    assert "train" in result.output
    assert "upload_to_s3" in result.output
