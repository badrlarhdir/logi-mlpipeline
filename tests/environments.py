import os
import pathlib
import shutil
from typing import Tuple

from click.testing import CliRunner

from mlpipeline.cli import cli
from mlpipeline.globals import PIPELINES_FOLDER

RESOURCES_FOLDER = 'tests/resources'

def init_dvc_env_folders(folder_name: str):
    ''' Initialize a simple example with the specified folder name

        Parameters
        ----------
        folder_name : str
            The folder name
    '''
    # check if folder_name is a list
    if isinstance(folder_name, list):
        for folder in folder_name:
            init_dvc_env_folders(folder)
    else:
        if pathlib.Path(folder_name).exists():
            shutil.rmtree(folder_name)
        if pathlib.Path(f'{RESOURCES_FOLDER}/{folder_name}').exists():
            shutil.copytree(f'{RESOURCES_FOLDER}/{folder_name}', f'./{folder_name}')
        
def init_dvc_env_files(file_name: str):
    ''' Initialize a simple example with the specified file name

        Parameters
        ----------
        file_name : str
            The file name
    '''
    # check if file_name is a list
    if isinstance(file_name, list):
        for file in file_name:
            init_dvc_env_files(file)
    else:
        if pathlib.Path(file_name).exists():
            os.remove(file_name)
        if pathlib.Path(f'{RESOURCES_FOLDER}/{file_name}').exists():
            shutil.copy(f'{RESOURCES_FOLDER}/{file_name}', f'./{file_name}')

def delete_dvc_env_folders(folder_name: str):
    ''' Delete a file with the specified folder name

        Parameters
        ----------
        folder_name : str
            The folder name
    '''
    # check if folder_name is a list
    if isinstance(folder_name, list):
        for folder in folder_name:
            delete_dvc_env_folders(folder)
    else:
        if pathlib.Path(folder_name).exists():
            shutil.rmtree(folder_name)

def delete_dvc_env_files(file_name: str):
    ''' Delete a file with the specified file name

        Parameters
        ----------
        file_name : str
            The file name
    '''
    # check if file_name is a list
    if isinstance(file_name, list):
        for file in file_name:
            delete_dvc_env_files(file)
    else:
        if pathlib.Path(file_name).exists():
            os.remove(file_name)

def clean_environment(status: str, pipeline: str = None):
    ''' Clean the environment from any previous test'''

    # Delete the pipelines folders if exists
    if status == 'start':
        init_dvc_env_folders(['.dvc', 'notebooks', 'data', 'outputs'])
        init_dvc_env_files(['dvc.yaml','.github/workflows/self-hosted-runner.yaml', 'params.yaml', '.dvcignore', 'dvc.lock', 'requirements.txt'])

    if status == 'end':
        delete_dvc_env_folders(['.dvc', 'notebooks', 'data', 'outputs'])
        delete_dvc_env_files(['dvc.yaml','.github/workflows/self-hosted-runner.yaml', 'params.yaml', '.dvcignore', 'dvc.lock', 'requirements.txt'])

    if pathlib.Path(PIPELINES_FOLDER).exists():
        shutil.rmtree(PIPELINES_FOLDER)

    # remove any file that has as prefix the name of the pipeline in .github/workflows folder
    if pathlib.Path(".github/workflows").exists():
        for file in os.listdir(".github/workflows"):
            if file.endswith("-self-hosted-runner.yaml"):
                os.remove(f".github/workflows/{file}")

def cleanEnv(func: callable):
    ''' Decorator to clean the environment from any previous test 
        and to clean the environment after the test
    '''
    
    def wrapper(*args, **kwargs):
        clean_environment('start')

        result = func(*args, **kwargs)

        clean_environment('end')
        return result
    return wrapper

def pipelineEnv(*pipelines: Tuple[str, ...]):
    '''Decorator to create a pipeline environment before the test 
        and to clean the environment after the test

        Parameters
        ----------
        *pipelines : Tuple[str, ...]
            The names of the pipelines to create
    '''

    def actual_decorator(func: callable):
        def wrapper(*args, **kwargs):
            clean_environment('start')

            runner = CliRunner()
            for pipeline in pipelines:
                result = runner.invoke(cli, ['create', '-p', pipeline])

            result = func(*args, **kwargs)

            clean_environment('end')
            return result
        return wrapper
    return actual_decorator

def linkedPipelineEnv(pipeline: str, notebooks: str):
    '''Decorator to create a pipeline environment linked to specified notebooks
        before the test and to clean the environment after the test

        Parameters
        ----------
        pipelines : str
            Name of the pipeline to create
        notebooks : str
            Names of the notebooks to link to the pipeline
    '''

    def actual_decorator(func: callable):
        def wrapper(*args, **kwargs):
            clean_environment('start', pipeline)

            runner = CliRunner()
            result = runner.invoke(cli, ['create',  '-p', pipeline, '-n', notebooks])

            result = func(*args, **kwargs)

            clean_environment('end', pipeline)
            return result
        return wrapper
    return actual_decorator
