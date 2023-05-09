import os
import subprocess

import requests

from .default import get_default_pipeline


def run_pipeline_cloud(
    pipeline: str, instance_type: str, ec2_target_size: int
):
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        print("Please set the GITHUB_TOKEN environment variable")
        return

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    data = {
        "event_type": f"mlpipeline-{pipeline}",
        "client_payload": {
            "EC2_INSTANCE_TYPE": instance_type,
            "EC2_TARGET_SIZE": ec2_target_size,
        },
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

    print("Running pipeline", pipeline, "...")

    response = requests.post(
        f"https://api.github.com/repos/{repo}/dispatches",
        headers=headers,
        json=data,
    )

    if response.status_code != 204:
        print("Error running pipeline", pipeline, "on the cloud")
        print(response.text)
        return

    print(response.text)


def run_cloud(pipeline: str, instance_type: str, ec2_target_size: int):
    """Run the pipeline on the cloud

    Parameters
        pipeline (str): name of the pipeline
    """

    if not pipeline:
        # Run the default pipeline
        pipeline = get_default_pipeline()

    if not instance_type:
        instance_type = "t2.micro"

    if not ec2_target_size:
        ec2_target_size = 30

    run_pipeline_cloud(pipeline, instance_type, ec2_target_size)
    return
