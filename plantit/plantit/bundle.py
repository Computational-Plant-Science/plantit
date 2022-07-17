import json

from asgiref.sync import async_to_sync
from django.contrib.auth.models import User

from plantit.github import has_github_info, get_user_github_profile, get_member_organizations
from plantit.redis import RedisClient
from plantit.users.models import Profile


def get_user_bundle(user: User):
    profile = Profile.objects.get(user=user)
    if not has_github_info(profile):
        return {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    else:
        redis = RedisClient.get()
        cached = redis.get(f"users/{user.username}")
        if cached is not None: return json.loads(cached)
        github_profile = async_to_sync(get_user_github_profile)(user)
        github_organizations = async_to_sync(get_member_organizations)(user)
        bundle = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'github_username': profile.github_username,
            'github_profile': github_profile,
            'github_organizations': github_organizations,
        } if 'login' in github_profile else {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        redis.set(f"users/{user.username}", json.dumps(bundle))
        return bundle