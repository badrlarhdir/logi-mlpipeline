import subprocess

from mlpipeline.globals import PIPELINES_FOLDER

from .sync import sync_pipeline
from .default import get_default_pipeline

def run_local(pipeline: str):
    ''' Run the dvc pipeline on the main project or on the selected pipeline
    
    Parameters
        (optional) pipeline (str): name of the pipeline
    '''

    if pipeline == 'main':
        print('Running main project...')
        subprocess.run(["dvc", "pull", "--allow-missing"])
        subprocess.run(["dvc", "repro", "-f"])

        # Reset dvc.lock file
        subprocess.run(["git", "reset", "--", "dvc.lock"])
        subprocess.run(["git", "checkout", "--", "dvc.lock"])

        print('Main project ran successfully')

        return

    # If no pipeline is specified, run the default pipeline
    if not pipeline:
        # Run the default pipeline
        pipeline = get_default_pipeline()

    # If a pipeline is specified OR if a default pipeline is found, run that pipeline
    if pipeline:
        print('Running pipeline', pipeline, '...')
        sync_pipeline(pipeline)

        subprocess.run('cd ' + PIPELINES_FOLDER + '/' + pipeline + ' && dvc pull --allow-missing && dvc repro -f', shell=True)

        path_pipeline_dvc_lock = f'./{PIPELINES_FOLDER}/{pipeline}/dvc.lock'

        print("Resetting dvc.lock file to the last commit...")
        # Reset dvc.lock file
        subprocess.run(["git", "reset", "--", path_pipeline_dvc_lock])
        subprocess.run(["git", "checkout", "--", path_pipeline_dvc_lock])

        print('Pipeline', pipeline, 'ran successfully')

        return
    
    print("Please specify a pipeline name to run, set a default pipeline using the default command or use the --main or -m flag to run the main project")
