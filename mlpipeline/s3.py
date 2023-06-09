import os
import shutil
import subprocess
from datetime import datetime

import boto3


def download_dvc_from_s3(s3_uri: str, local_path: str, download: bool = False):
    """
    Download a file or directory from a s3 URL (s3://) into the local file system.
    Parameters
        s3_uri: the folder path in the s3 bucket or the s3 uri of the file
        local_path: a relative directory path in the local file system (ex: ./data/sw_folder/) or
            the local output name of the file with a specific path (ex: ./data/data.csv)
    """
    # Download the file from s3
    # !dvc import-url s3_uri local_path --no-download
    if not download:
        subprocess.run(
            ["dvc", "import-url", s3_uri, local_path, "--no-download"]
        )
    else:
        subprocess.run(["dvc", "import-url", s3_uri, local_path])


def download_from_s3(s3_uri: str, local_path: str):
    """
    Download a file or directory from a s3 URL (s3://) into the local file system.
    Parameters
        s3_uri: the folder path in the s3 bucket or the s3 uri of the file
        local_path: a relative directory path in the local file system (ex: ./data/sw_folder/) or
            the local output name of the file with a specific path (ex: ./data/data.csv)
    """
    # Download the file from s3
    # !aws s3 cp s3_uri local_path --recursive
    subprocess.run(["aws", "s3", "cp", s3_uri, local_path, "--recursive"])


def delete_file_or_folder(path: str, delete: bool = False):
    """
    Delete a file from the local file system
    Parameters
        path: the path of the file to delete
    """
    # Delete the file
    subprocess.run(["dvc", "remove", f"{path}.dvc"])
    if delete:
        if os.path.isdir(path):
            shutil.rmtree(path)
        if os.path.isfile(path):
            os.remove(path)


def upload_folder_to_s3(s3_bucket_name: str, s3_folder: str, folder_path: str):
    """
    Upload the outputs of the pipeline to an s3 bucket
    Parameters
        s3_bucket_name: the name of the s3 bucket
        s3_folder: the name of the folder in the s3 bucket
        folder_path: the path of the folder to upload
    """
    # Push the files to s3

    print("Uploading outputs to s3...")

    s3 = boto3.client("s3")

    # Define bucket and folder names
    date_string = datetime.now().strftime("%a_%B_%d_%Y_%H-%M-%S_UTC")
    experiment_id = (
        f'{os.environ.get("EXPERIMENT_ID")}_'
        if os.environ.get("EXPERIMENT_ID")
        else ""
    )
    ec2_instance_type = (
        f'{os.environ.get("EC2_INSTANCE_TYPE")}_'
        if os.environ.get("EC2_INSTANCE_TYPE")
        else ""
    )

    # if s3_folder is empty string then don't add a slash
    if s3_folder:
        folder_name = (
            f"{s3_folder}/{ec2_instance_type}{experiment_id}{date_string}/"
        )
    else:
        folder_name = f"{ec2_instance_type}{experiment_id}{date_string}/"

    # Upload the contents of the local folder to S3
    for subdir, _, files in os.walk(folder_path):
        for file in files:
            # check if file doesn't start with .git
            if not file.startswith(".git"):
                file_path = os.path.join(subdir, file)
                s3_key = os.path.relpath(file_path, folder_path)
                s3.upload_file(
                    file_path, s3_bucket_name, f"{folder_name}{s3_key}"
                )

    print("Outputs uploaded to s3")
