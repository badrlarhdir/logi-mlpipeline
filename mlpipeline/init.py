import os
import pathlib
import shutil
import subprocess


def init():
    """Initialize the project repository with the required folders and files"""

    # Initialize dvc
    # verify that .dvc does not exist
    if not pathlib.Path(".dvc").exists():
        subprocess.run(["dvc", "init"])

    # Add .gitignore file if it does not exist
    if not pathlib.Path(".gitignore").exists():
        # Copy from the .gitignore.txt file in the package
        shutil.copyfile(
            os.path.join(
                os.path.dirname(__file__), "resources/.gitignore.txt"
            ),
            ".gitignore",
        )

    # Create data folder
    if not pathlib.Path("data").exists():
        os.makedirs("data")

    # Add .gitignore file if it does not exist data folder
    if not pathlib.Path("./data/.gitignore").exists():
        with open("./data/.gitignore", "w") as gitignore_f:
            gitignore_f.write(
                "# Ignores all data files in the data folder\n# Except the .dvc extension files\n"
            )

    # Create notebooks folder
    if not pathlib.Path("notebooks").exists():
        os.makedirs("notebooks")

    # Create outputs folder
    if not pathlib.Path("outputs").exists():
        os.makedirs("outputs")
        # create a .gitkeep file to keep the folder in git
        pathlib.Path("outputs/.gitkeep").touch()

    print("Project initialized")
