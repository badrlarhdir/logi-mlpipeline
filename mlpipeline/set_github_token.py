import os
import pathlib

def set_github_token(token: str):
    ''' Get the status of the cloud instance
    
    Parameters
        token (str): github PAT 
    '''
    
    # Write the token to the environment variable file (.env)

    # Delete the file if it exists
    if pathlib.Path(".env").exists():
        os.remove(".env")

    # Create the file
    with open(".env", "w") as f:
        f.write(f"GITHUB_TOKEN={token}\n")

