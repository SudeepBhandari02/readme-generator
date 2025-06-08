from app.utils import clone_repo
import os

def generate_readme_from_repo(repo_url: str) -> str:
    repo_path = clone_repo(repo_url)

    file_data = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.md', '.txt', '.json')):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        file_data.append(f"## File: {file}\n{content}")
                except Exception as e:
                    print(f"Skipping file {file}: {e}")

    
    full_text = "\n\n".join(file_data)
    short_text = full_text[:3000]  

    return f"# Auto-Generated README\n\nThis repo contains:\n\n{short_text}"
