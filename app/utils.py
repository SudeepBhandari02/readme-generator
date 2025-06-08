import os
import shutil
import tempfile
from git import Repo

def clone_repo(repo_url: str) -> str:
    temp_dir = tempfile.mkdtemp()
    try:
        Repo.clone_from(repo_url, temp_dir)
        print(f"Repo cloned to: {temp_dir}")
        return temp_dir
    except Exception as e:
        print("Failed to clone repo:", e)
        shutil.rmtree(temp_dir)
        raise e
