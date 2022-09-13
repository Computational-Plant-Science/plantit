import logging
import traceback
from datetime import datetime

import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from pycyapi.clients import TerrainClient
from pycyapi.exceptions import Unauthorized

logger = logging.getLogger(__name__)


def get_user_cyverse_profile(user: User) -> dict:
    client = TerrainClient(user.profile.cyverse_access_token)
    profile = client.user_info(user.username)
    if profile is None: raise ValueError(f"User {user.username} has no CyVerse profile")

    altered = False
    if profile['first_name'] != user.first_name:
        user.first_name = profile['first_name']
        altered = True
    if profile['last_name'] != user.last_name:
        user.last_name = profile['last_name']
        altered = True
    if profile['institution'] != user.profile.institution:
        user.profile.institution = profile['institution']
        altered = True

    # only write to DB if we change anything (avoids a network call if we don't need one)
    if altered:
        user.profile.save()
        user.save()

    return profile


def refresh_user_cyverse_tokens(user: User):
    if user.profile.cyverse_refresh_token is None:
        logger.warning(f"User {user.username} has no CyVerse access token to refresh")
        return

    try:
        client = TerrainClient(user.profile.cyverse_access_token)
        access_token, refresh_token = client.refresh_tokens(
            username=user.username,
            client_id=settings.CYVERSE_CLIENT_ID,
            client_secret=settings.CYVERSE_CLIENT_SECRET,
            refresh_token=user.profile.cyverse_refresh_token,
            redirect_uri=settings.CYVERSE_REDIRECT_URL)
    except Unauthorized as e:
        decoded = jwt.decode(user.profile.cyverse_refresh_token, options={
            'verify_signature': False,
            'verify_aud': False,
            'verify_iat': False,
            'verify_exp': False,
            'verify_iss': False
        })
        exp = datetime.fromtimestamp(decoded['exp'], timezone.utc)
        now = datetime.now(tz=timezone.utc)

        if now > exp:
            logger.warning(f"CyVerse refresh token for {user.username} expired at {exp.isoformat()}, can't refresh access token")
        else:
            logger.error(f"Failed to refresh CyVerse access token for {user.username}: {e.message}")
        return
    except Exception:
        logger.error(f"Failed to refresh CyVerse access token for {user.username}: {traceback.format_exc()}")
        return

    user.profile.cyverse_access_token = access_token
    user.profile.cyverse_refresh_token = refresh_token
    user.profile.save()
    user.save()
