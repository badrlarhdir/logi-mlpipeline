import subprocess

from .sync import sync_pipeline

def publish(pipeline: str, message: str):
    ''' Run the dvc pipeline on the main project or on the selected pipeline
    
    Parameters
        (optional) pipeline (str): name of the pipeline
    '''
    
    if pipeline:
        print('Publishing pipeline', pipeline, '...')
        sync_pipeline(pipeline)

        # Add only the folder of the pipeline and the pipelines.json file inside the pipelines folder
        subprocess.run(["git", "add", f"./pipelines/{pipeline}", "./pipelines/pipelines.json"])

        # Add all the files inside .github/workflows that starts with the pipeline name
        subprocess.run(["git", "add", f'./.github/workflows/{pipeline}*'])

        commit_message = f'Publishing pipeline {pipeline}: {message}'
        print('Commiting changes with message:', commit_message)
        subprocess.run(["git", "commit", "-m", commit_message])
        
        print('Pushing changes to remote repository')
        subprocess.run(["git", "push"])
        return
    
    # Publish the whole project
    print('Publishing the project ...')
    sync_pipeline()
    subprocess.run(["git", "add", '.'])
    subprocess.run(["git", "commit", "-m", commit_message])
    subprocess.run(["git", "push"])
    return