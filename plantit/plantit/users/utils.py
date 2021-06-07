import logging

import requests
from django.contrib.auth.models import User

from plantit.terrain import refresh_tokens, get_profile

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


def get_cyverse_profile(user: User) -> dict:
    profile = get_profile(user.username, user.profile.cyverse_access_token)
    altered = False
    if profile['first_name'] != user.first_name: user.first_name = profile['first_name']
    if profile['last_name'] != user.last_name: user.last_name = profile['last_name']
    if altered: user.save()

    return profile


def refresh_cyverse_tokens(user: User):
    access_token, refresh_token = refresh_tokens(username=user.username, refresh_token=user.profile.cyverse_refresh_token)
    user.profile.cyverse_access_token = access_token
    user.profile.cyverse_refresh_token = refresh_token
    user.profile.save()
    user.save()


def get_github_profile(user: User):
    response = requests.get(f"https://api.github.com/users/{user.profile.github_username}",
                                   headers={'Authorization':
                                                f"Bearer {user.profile.github_token}"})
    if response.status_code == 200:
        return response.json()
    else:
        logger.warning(f"Bad response from GitHub for user {user.profile.github_username}: {response.status_code}")
        return None
