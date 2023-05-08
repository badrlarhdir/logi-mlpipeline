from click.testing import CliRunner

from mlpipeline.cli import cli

from .environments import cleanEnv, pipelineEnv
from .globals import EXIT_CODE_SUCCESS

# ---------------------------------------------------------------------------- #
#                           Test on the list command                           #
# ---------------------------------------------------------------------------- #

# ----------------------------- Clean Environment ---------------------------- #

@cleanEnv
def test_list_clean_env():
    ''' Test the list command in a clean environment '''

    runner = CliRunner()
    result = runner.invoke(cli, ['list'])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "No pipelines found" in result.output

# ----------------------------- Pipeline Created ----------------------------- #

@pipelineEnv('myfirstpipeline')
def test_list_with_1_existing_pipeline():
    ''' Test the sync commands with a pipeline that exists '''

    runner = CliRunner()
    result = runner.invoke(cli, ['list'])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline: myfirstpipeline" in  result.output

@pipelineEnv('myfirstpipeline', 'mysecondpipeline', 'mythirdpipeline')
def test_list_with_3_existing_pipeline():
    ''' Test the sync commands with three pipelines that exist '''

    runner = CliRunner()
    result = runner.invoke(cli, ['list'])

    assert result.exit_code == EXIT_CODE_SUCCESS
    assert "Pipeline: myfirstpipeline" in  result.output
    assert "Pipeline: mysecondpipeline" in  result.output
    assert "Pipeline: mythirdpipeline" in  result.output
