import json
import os
import subprocess

import requests

from .default import get_default_pipeline


def run_pipeline_cloud(
    pipeline: str, instance_type: str, ec2_target_size: int, branch: str
):
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        print("Please set the GITHUB_TOKEN environment variable")
        return

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
    }

    payload = {
        "ref": branch,
        "inputs": {
            "EC2_INSTANCE_TYPE": instance_type,
            "EC2_TARGET_SIZE": str(ec2_target_size),
            "PIPELINE": pipeline,
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

    # Run workflow_dispatch event
    response = requests.post(
        f"https://api.github.com/repos/{repo}/actions/workflows/matrix.yaml/dispatches",
        headers=headers,
        json=payload,
    )

    if response.status_code != 204:
        print("Error running pipeline", pipeline, "on the cloud")
        print(response.text)
        return

    print(response.text)


def run_cloud(
    pipeline: str, instance_type: str, ec2_target_size: int, branch: str
):
    """Run the pipeline on the cloud

    Parameters
        pipeline (str): name of the pipeline
    """

    if not pipeline:
        # Run the default pipeline
        pipeline = get_default_pipeline()
        if not pipeline:
            return

    if not instance_type:
        instance_type = "['t2.micro']"

    if not ec2_target_size:
        ec2_target_size = 30

    # Get the default branch name with an API call to github
    if not branch:
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

        url = f"https://api.github.com/repos/Logitech/sw-data-mlops-internship"

        token = os.getenv("GITHUB_TOKEN")

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {token}",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            repo_info = json.loads(response.text)
            branch = repo_info["default_branch"]
            if not branch:
                print("Failed to fetch the default branch of the repository")
                return
        else:
            print(
                f"Failed to fetch repository information. Status code: {response.status_code}"
            )
            return

    run_pipeline_cloud(pipeline, instance_type, ec2_target_size, branch)
    return
