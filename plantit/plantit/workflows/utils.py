import httpx

from plantit.utils import get_repo_config, get_repo_readme


def refresh_workflow(username, name, token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }

    with httpx.Client(headers=headers) as client:
        response = client.get(f"https://api.github.com/repos/{username}/{name}")
        repo = response.json()
        owner = repo['owner']['login']
        name = repo['name']
        return {
            'repo': repo,
            'config': get_repo_config(name, owner, token),
            # 'readme': get_repo_readme(name, owner, token)
        }