import logging

import requests
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


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


def get_cyverse_profile(user: User):
    response = requests.get(
        f"https://de.cyverse.org/terrain/secured/user-info?username={user.username}",
        headers={'Authorization': f"Bearer {user.profile.cyverse_token}"})
    if response.status_code == 401:
        return 'expired token'
    else:
        content = response.json()
        if user.username in content:
            profile = response.json()[user.username]
            user.first_name = profile['first_name']
            user.last_name = profile['last_name']
            user.save()
            return profile
        else:
            logger.warning(f"User {user.username} has no CyVerse profile")
            return None


def get_github_profile(user: User):
    response = requests.get(f"https://api.github.com/users/{user.profile.github_username}",
                                   headers={'Authorization':
                                                f"Bearer {user.profile.github_token}"})
    if response.status_code == 200:
        return response.json()
    else:
        logger.warning(f"Bad response from GitHub for user {user.profile.github_username}: {response.status_code}")
        return None
