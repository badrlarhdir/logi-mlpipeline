from __future__ import annotations

import os
import pathlib

import click

from .create import *
from .default import *
from .delete import *
from .init import *
from .link import *
from .list import *
from .run_cloud import *
from .run_local import *
from .set_github_token import *
from .show import *
from .sync import *
from .utils import *


def load_env():
    """Load the environment variables from the .env file"""

    if pathlib.Path(".env").exists():
        with open(".env") as f:
            for line in f:
                # Remove any leading/trailing whitespace and ignore comments and empty lines
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Split the line into key and value
                key, value = line.split("=", 1)

                # Add the key and value to the environment
                os.environ[key] = value


load_env()


@click.group(name="package")
def cli():
    pass


@click.command("init")
def __init():
    """Initialize the project repository with the required folders and files"""

    init()


@click.command("sync")
@click.option("--notebooks", "-n", help="List of notebooks in the pipeline")
@click.option("--pipeline", "-p", help="Name of the pipeline")
@click.option(
    "--force",
    "-f",
    help="Forces creation of a new params.yaml file",
    is_flag=True,
)
@click.option(
    "--all",
    "-a",
    help="Sync all the pipelines",
    is_flag=True,
)
def __sync(
    notebooks: str | None,
    pipeline: str | None,
    force: bool | None,
    all: bool | None,
):
    """Sync the notebooks with the pipeline project or the main project

    Parameters
        (optional) notebooks (str | None): list of notebooks in the pipeline
        (optional) pipeline (str | None): name of the pipeline
        (optional) force (bool | None): forces creation of a new params.yaml file (default: False)
        (optional) all (bool | None): sync all the pipelines (default: False)
    """

    sync(notebooks, pipeline, force, all)


@click.command("delete")
@click.option("--pipeline", "-p", help="Name of the pipeline", required=False)
@click.option("--all", "-a", help="Remove all pipelines", is_flag=True)
def __delete(pipeline: str, all: bool):
    """Deletes a pipeline or all the pipelines

    Param
        (optional) pipeline (str): name of the pipeline
        (optional) all (bool): remove all pipelines
    """

    delete(pipeline, all)


@click.command("create")
@click.option("--pipeline", "-p", help="Name of the pipeline", required=True)
@click.option("--notebooks", "-n", help="List of notebooks in the pipeline")
def __create(pipeline: str, notebooks: str):
    """Create a pipeline project

    Param
        (optional) notebooks (str): list of notebooks in the pipeline
        pipeline (str): name of the pipeline
    """

    create(pipeline, notebooks)


@click.command("list")
def __list_pipelines():
    """List the pipelines"""

    list_pipelines()


@click.command("link")
@click.option(
    "--notebooks",
    "-n",
    help="List of notebooks in the pipeline",
    required=True,
)
@click.option("--pipeline", "-p", help="Name of the pipeline", required=True)
def __link(notebooks: str, pipeline: str):
    """Link the notebooks to the selected pipeline

    Param
        notebooks (str): list of notebooks in the pipeline
        pipeline (str): name of the pipeline
    """

    link_notebooks_to_pipeline(notebooks, pipeline)


@click.command("show")
@click.option("--pipeline", "-p", help="Name of the pipeline", required=False)
def __show(pipeline: str):
    """Show the pipeline graph in the terminal"""

    show(pipeline)


@click.command("run_local")
@click.option("--pipeline", "-p", help="Name of the pipeline", required=False)
def __run_local(pipeline: str):
    """Run the dvc pipeline on the main project or on the selected pipeline

    Param
        (optional) pipeline (str): name of the pipeline
    """

    run_local(pipeline)


@click.command("default")
@click.option("--pipeline", "-p", help="Name of the pipeline", required=True)
def __set_default_pipeline(pipeline: str):
    """Set the default pipeline to be used when no pipeline is specified

    Param
        (optional) pipeline (str): name of the pipeline
    """

    set_default_pipeline(pipeline)


@click.command("run_cloud")
@click.option("--pipeline", "-p", help="Name of the pipeline", required=False)
@click.option(
    "--instance_type", "-i", help="EC2 instance type", required=False
)
@click.option(
    "--size", "-s", help="EC2 instance size", required=False, type=int
)
@click.option("--branch", "-b", help="Branch name", required=False, type=str)
def __run_cloud(pipeline: str, instance_type: str, size: int, branch: str):
    """Run the pipeline on the cloud

    Param
        pipeline (str): name of the pipeline
    """

    run_cloud(pipeline, instance_type, size, branch)


@click.command("set_token")
@click.option(
    "--token", "-t", help="Github's Personnal Access token", required=True
)
def __set_github_token(token: str):
    """Get the status of the cloud instance

    Param
        token (str): github PAT
    """

    set_github_token(token)


cli.add_command(__init)
cli.add_command(__sync)
cli.add_command(__show)
cli.add_command(__delete)
cli.add_command(__create)
cli.add_command(__link)
cli.add_command(__list_pipelines)
cli.add_command(__run_local)
cli.add_command(__set_default_pipeline)
cli.add_command(__run_cloud)
cli.add_command(__set_github_token)
