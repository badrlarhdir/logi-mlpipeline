import os
import subprocess

import requests
from tabulate import tabulate

from .default import get_default_pipeline


def cloud_status(pipeline: str):
    """Run the pipeline on the cloud

    Parameters
        pipeline (str): name of the pipeline
    """

    if not pipeline:
        # Run the default pipeline
        pipeline = get_default_pipeline()

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Please set the GITHUB_TOKEN environment variable")
        return

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {token}",
    }

    data = {
        "event_type": f"mlpipeline-{pipeline}",
    }

    # Get the repository name from the remote url
    repo = (
        subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"]
        )
        .decode("utf-8")
        .strip()
    )
    repo = repo.split("/")[-2:]
    repo = "/".join(repo).replace(".git", "")

    response = requests.get(
        f"https://api.github.com/repos/{repo}/actions/runs",
        headers=headers,
        json=data,
    )

    # Transform the response to json
    response = response.json()

    # Filter the response to get only the display_title equal to the pipeline name
    response = [
        x
        for x in response["workflow_runs"]
        if x["display_title"] == f"mlpipeline-{pipeline}"
    ]

    # Get the last run
    if len(response) == 0:
        print("No runs found")
        return

    table_result = [
        ["Id", "Head_branch", "Actor", "Status", "Conclusion"],
        [
            response[0]["id"],
            response[0]["head_branch"],
            response[0]["actor"]["login"],
            response[0]["status"],
            response[0]["conclusion"],
        ],
    ]

    print(tabulate(table_result, headers="firstrow", tablefmt="presto"))

    return
