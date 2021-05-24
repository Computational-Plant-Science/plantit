import requests


def list_users(queryset, github_token):
    users = []
    for user in list(queryset.exclude(profile__isnull=True)):
        if user.profile.github_username:
            github_profile = requests.get(f"https://api.github.com/users/{user.profile.github_username}",
                                          headers={'Authorization': f"Bearer {github_token}"}).json()
            if 'login' in github_profile:
                users.append({
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'github_username': user.profile.github_username,
                    'github_profile': github_profile
                })
            else:
                users.append({
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                })
        else:
            users.append({
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
            })

    return users


def get_user_stats(username: str):
    return {
        'most_used_cluster': 'Sapelo2',
        'most_used_dataset': 'phenome_force_spg',
        'most_frequent_collaborator': 'Suxing Liu'
    }
