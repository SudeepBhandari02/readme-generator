from fastapi import FastAPI
from pydantic import BaseModel

from app.rag_pipeline import generate_readme_from_repo

app = FastAPI()

class GitHubInput(BaseModel):
    repo_url: str

@app.post("/generate-readme")
def generate_readme(input: GitHubInput):
    readme = generate_readme_from_repo(input.repo_url)
    return {"readme": readme}
