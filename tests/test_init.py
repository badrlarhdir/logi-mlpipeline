import pathlib

from click.testing import CliRunner

from mlpipeline.cli import cli

from .environments import emptyEnv, initializedEnv
from .globals import EXIT_CODE_SUCCESS

# ---------------------------------------------------------------------------- #
#                          Test on the init command                          #
# ---------------------------------------------------------------------------- #

# ----------------------------- Empty Environment ---------------------------- #


@emptyEnv
def test_init_on_empty_env():
    """Test the init command in an empty environment"""

    runner = CliRunner()
    result = runner.invoke(cli, ["init"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Project initialized" in result.output


# ----------------------------- Initialized Environment ---------------------------- #


@initializedEnv
def test_init_on_already_init_env():
    """Test the init command in an environment that was already initialized
    i.e it should not brake anything and should not display any error message
    """

    runner = CliRunner()
    result = runner.invoke(cli, ["init"])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Project initialized" in result.output
