import requests
import yaml


def get_repo_config(name: str, owner: str, token: str) -> dict:
    print(f"Getting config for {owner}/{name}")
    request = requests.get(
        f"https://api.github.com/repos/{owner}/{name}/contents/plantit.yaml") if token == '' \
        else requests.get(f"https://api.github.com/repos/{owner}/{name}/contents/plantit.yaml",
                          headers={"Authorization": f"token {token}"})
    file = request.json()
    content = requests.get(file['download_url']).text
    config = yaml.load(content)

    # fill optional attributes
    config['public'] = config['public'] if 'public' in config else True

    return config


def get_repo_readme(name: str, owner: str, token: str) -> str:
    print(f"Getting README for {owner}/{name}")
    try:
        url = f"https://api.github.com/repos/{owner}/{name}/contents/README.md"
        request = requests.get(url) if token == '' else requests.get(url, headers={"Authorization": f"token {token}"})
        file = request.json()
        return requests.get(file['download_url']).text
    except:
        try:
            url = f"https://api.github.com/repos/{owner}/{name}/contents/README"
            request = requests.get(url) if token == '' else requests.get(url, headers={"Authorization": f"token {token}"})
            file = request.json()
            return requests.get(file['download_url']).text
        except:
            return None