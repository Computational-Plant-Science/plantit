import json
import logging
import os
import traceback
from urllib.parse import parse_qs
from urllib.parse import urlencode

import jwt
import requests
from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from github import Github
from requests import HTTPError
from requests.auth import HTTPBasicAuth
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from databases import Database
from pycyapi.clients import TerrainClient

import plantit.queries as q
from plantit.celery_tasks import migrate_dirt_datasets, Migration
from plantit.celery_tasks import refresh_user_stats
from plantit.keypairs import get_or_create_user_keypair
from plantit.redis import RedisClient
from plantit.sns import SnsClient, get_sns_subscription_status
from plantit.users.models import Profile
from plantit.users.serializers import UserSerializer
from plantit.utils.misc import get_csrf_token

logger = logging.getLogger(__name__)


class IDPViewSet(viewsets.ViewSet):
    swagger_schema = None
    permission_classes = (AllowAny,)
    logger = logging.getLogger(__name__)

    def get_object(self):
        return self.request.user

    @action(methods=['get'], detail=False)
    def cyverse_login(self, request):
        return redirect('https://kc.cyverse.org/auth/realms/CyVerse/protocol/openid-connect/auth?client_id=' +
                        os.environ.get('CYVERSE_CLIENT_ID') +
                        '&redirect_uri=' +
                        os.environ.get('CYVERSE_REDIRECT_URL') +
                        '&response_type=code')

    @action(methods=['get'], detail=False)
    def cyverse_logout(self, request):
        logout(request)
        return redirect("https://kc.cyverse.org/auth/realms/CyVerse/protocol/openid-connect/logout?redirect_uri=https"
                        "%3A%2F%2Fkc.cyverse.org%2Fauth%2Frealms%2FCyVerse%2Faccount%2F")

    @action(methods=['get'], detail=False)
    def cyverse_handle_temporary_code(self, request):
        session_state = request.GET.get('session_state', None)
        code = request.GET.get('code', None)

        # missing session state string or code indicates a mis-configured redirect from the KeyCloak client?
        if session_state is None: return HttpResponseBadRequest("Missing param: 'session_state'")
        if code is None: return HttpResponseBadRequest("Missing param: 'code'")

        # send the authorization request
        response = requests.post("https://kc.cyverse.org/auth/realms/CyVerse/protocol/openid-connect/token", data={
            'grant_type': 'authorization_code',
            'client_id': os.environ.get('CYVERSE_CLIENT_ID'),
            'code': code,
            'redirect_uri': os.environ.get('CYVERSE_REDIRECT_URL')},
                                 auth=HTTPBasicAuth(request.user.username, os.environ.get('CYVERSE_CLIENT_SECRET')))

        # if we have anything other than a 200 the auth request did not succeed
        if response.status_code == 400: return HttpResponse('Unauthorized for KeyCloak token endpoint', status=401)
        elif response.status_code != 200: return HttpResponse('Bad response from KeyCloak token endpoint', status=500)

        # get the response body
        content = response.json()

        # make sure we have CyVerse access & refresh tokens
        if 'access_token' not in content: return HttpResponseBadRequest(
            "Missing param on token response: 'access_token'")
        if 'refresh_token' not in content: return HttpResponseBadRequest(
            "Missing param on token response: 'refresh_token'")

        # decode them
        access_token = content['access_token']
        refresh_token = content['refresh_token']
        decoded_access_token = jwt.decode(access_token, options={
            'verify_signature': False,
            'verify_aud': False,
            'verify_iat': False,
            'verify_exp': False,
            'verify_iss': False
        })
        decoded_refresh_token = jwt.decode(refresh_token, options={
            'verify_signature': False,
            'verify_aud': False,
            'verify_iat': False,
            'verify_exp': False,
            'verify_iss': False
        })

        # retrieve the user entry (or create if it's their first time logging in)
        user, _ = User.objects.get_or_create(username=decoded_access_token['preferred_username'])

        # update the user's personal info
        user.first_name = decoded_access_token['given_name']
        user.last_name = decoded_access_token['family_name']
        user.email = decoded_access_token['email']
        user.save()

        # update the user's profile (CyVerse tokens, etc)
        profile, created = Profile.objects.get_or_create(user=user)
        if created: profile.created = timezone.now()
        profile.cyverse_access_token = access_token
        profile.cyverse_refresh_token = refresh_token
        user.profile = profile
        profile.save()
        user.save()

        # if user's stats haven't been calculated yet, schedule it
        redis = RedisClient.get()
        cached_stats = redis.get(f"stats/{user.username}")
        if cached_stats is None:
            self.logger.info(f"No usage statistics for {user.username}. Scheduling refresh...")
            refresh_user_stats.s(user.username).apply_async()

        # log the user into the builtin django backend
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        # open the dashboard
        return redirect(f"/home/")

    @action(methods=['get'], detail=False)
    def github_request_identity(self, request):
        return redirect(settings.GITHUB_AUTH_URI + '?' + urlencode({
            'client_id': settings.GITHUB_CLIENT_ID,
            'redirect_uri': settings.GITHUB_REDIRECT_URI,
            'state': get_csrf_token(request),
            'scope': 'repo'}))

    @action(methods=['get'], detail=False)
    def github_handle_temporary_code(self, request):
        state = request.GET.get('state', None)
        error = request.GET.get('error', None)
        if error == 'access_denied':
            return HttpResponseBadRequest()
        if state is None:
            return HttpResponseBadRequest()
        elif state != get_csrf_token(request):
            return HttpResponse('unauthorized', status=401)

        code = request.GET.get('code', None)
        if code is None:
            return HttpResponseBadRequest()

        response = requests.post('https://github.com/login/oauth/access_token', data={
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_SECRET,
            'redirect_uri': settings.GITHUB_REDIRECT_URI,
            'code': code})

        token = parse_qs(response.text)['access_token'][0]
        user = self.get_object()
        profile = Profile.objects.get(user=user)
        profile.github_username = Github(token).get_user().login
        profile.github_token = token
        profile.save()
        user.save()

        return redirect(f"/home/")


class UsersViewSet(viewsets.ModelViewSet, mixins.RetrieveModelMixin):
    swagger_schema = None
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    logger = logging.getLogger(__name__)

    def get_object(self):
        return self.request.user

    @action(detail=False, methods=['get'])
    def get_all(self, request):
        return JsonResponse({'users': q.list_users()})

    @action(methods=['get'], detail=False)
    def acknowledge_first_login(self, request):
        user = self.get_object()
        user.profile.first_login = False
        user.profile.save()
        user.save()
        return HttpResponse(status=200)

    @action(detail=False, methods=['get'])
    def toggle_push_notifications(self, request):
        user = request.user
        sns = SnsClient.get()
        topic_name = f"plantit-push-notifications-{user.username}"

        if user.profile.push_notification_status == 'disabled':
            topic = sns.create_topic(topic_name)
            subscription = sns.subscribe(topic['TopicArn'], 'email', user.email)
            user.profile.push_notification_topic_arn = topic['TopicArn']
            user.profile.push_notification_sub_arn = subscription['SubscriptionArn']
            user.profile.push_notification_status = 'pending'
            user.profile.save()
            user.save()

            return JsonResponse({'push_notifications': user.profile.push_notification_status})
        else:
            sub_status = get_sns_subscription_status(user.profile.push_notification_topic_arn)
            if sub_status == 'pending':
                user.profile.push_notification_status = 'pending'
                user.profile.save()
                user.save()
                return JsonResponse({'push_notifications': sub_status})
            else:
                sns.delete_subscription(user.profile.push_notification_sub_arn)
                sns.delete_topic(user.profile.push_notification_topic_arn)
                user.profile.push_notification_topic_arn = None
                user.profile.push_notification_sub_arn = None
                user.profile.push_notification_status = 'disabled'
                user.profile.save()
                user.save()
                return JsonResponse({'push_notifications': user.profile.push_notification_status})

    @action(detail=False, methods=['get'])
    def toggle_hints(self, request):
        user = request.user
        user.profile.hints = not user.profile.hints
        user.profile.save()
        user.save()
        return JsonResponse({'hints': user.profile.hints})

    @action(detail=False, methods=['get'])
    def toggle_dark_mode(self, request):
        user = request.user
        user.profile.dark_mode = not user.profile.dark_mode
        user.profile.save()
        user.save()
        return JsonResponse({
            'dark_mode': user.profile.dark_mode
        })

    @action(detail=False, methods=['get'])
    def get_current(self, request):
        user = request.user

        # TODO: reenable
        if user.profile.push_notification_status == 'pending':
            user.profile.push_notification_status = get_sns_subscription_status(user.profile.push_notification_topic_arn)
            user.profile.save()
            user.save()

        migration, created = Migration.objects.get_or_create(profile=user.profile)
        if created:
            migration.downloads = json.dumps([])
            migration.uploads = json.dumps([])
            migration.save()

        response = {
            'django_profile': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'dark_mode': user.profile.dark_mode,
                'push_notifications': user.profile.push_notification_status,
                'github_token': user.profile.github_token,
                'cyverse_token': user.profile.cyverse_access_token,
                'hints': user.profile.hints,
                'first': user.profile.first_login,
                'migration': q.migration_to_dict(migration)
            },
            'stats': async_to_sync(q.get_user_statistics)(user),
            'users': q.list_users(),
            'tasks': q.get_tasks(user, page=1),
            'delayed_tasks': q.get_delayed_tasks(user),
            'repeating_tasks': q.get_repeating_tasks(user),
            'triggered_tasks': q.get_triggered_tasks(user),
            'notifications': q.get_notifications(user, page=1),
            'agents': q.get_agents(user),
            'workflows': {
                'public': q.list_public_workflows(),
                'project': q.list_user_project_workflows(user)
            },
            'projects': q.get_user_projects(user),
        }

        if request.user.profile.cyverse_access_token != '':
            # if we can't get a profile from CyVerse, log the user out ( sorry :/ )
            try: response['cyverse_profile'] = q.get_user_cyverse_profile(request.user)
            except (HTTPError, ValueError) as e:
                if '403' in str(e) or 'no CyVerse profile' in str(e):
                    logout(request)
                    return redirect(
                        "https://kc.cyverse.org/auth/realms/CyVerse/protocol/openid-connect/logout?redirect_uri=https"
                        "%3A%2F%2Fkc.cyverse.org%2Fauth%2Frealms%2FCyVerse%2Faccount%2F")
                else: raise

        profile = Profile.objects.get(user=request.user)
        if q.has_github_info(profile):
            try:
                response['github_profile'] = async_to_sync(q.get_user_github_profile)(user)
                response['organizations'] = async_to_sync(q.get_user_github_organizations)(user)
                response['workflows']['user'] = q.list_user_workflows(profile.github_username)
                response['workflows']['org'] = async_to_sync(q.list_user_org_workflows)(user)
            except:
                logger.warning(f"Failed to load Github info for user {request.user.username}: {traceback.format_exc()}")
                response['github_profile'] = None
                response['organizations'] = []
        else:
            response['github_profile'] = None
            response['organizations'] = []

        return JsonResponse(response)

    @action(detail=False, methods=['get'])
    def get_by_username(self, request):
        username = request.GET.get('username', None)

        # TODO move to configuration file
        if username == 'Computational-Plant-Science' or username == 'van-der-knaap-lab' or username == 'burkelab':
            if request.user.profile.github_token != '':
                github_response = requests.get(f"https://api.github.com/users/{username}",
                                               headers={'Authorization':
                                                            f"Bearer {request.user.profile.github_token}"})
                return JsonResponse({
                    'django_profile': None,
                    'cyverse_profile': None,
                    'github_profile': github_response.json()
                })
            else:
                return JsonResponse({
                    'django_profile': None,
                    'cyverse_profile': None,
                })

        user = self.queryset.get(owner=username)
        response = {
            'django_profile': {
                'username': username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }

        if request.user.username == user.username:
            response['django_profile']['cyverse_token'] = user.profile.cyverse_access_token

        if request.user.profile.cyverse_access_token != '':
            cyverse_response = requests.get(
                f"https://de.cyverse.org/terrain/secured/user-info?username={user.username}",
                headers={'Authorization': f"Bearer {request.user.profile.cyverse_access_token}"})
            if cyverse_response.status_code == 401:
                response['cyverse_profile'] = 'expired token'
            else:
                cyverse_profile = cyverse_response.json()
                if user.username in cyverse_profile:
                    response['cyverse_profile'] = cyverse_response.json()[user.username]
                    user.first_name = response['cyverse_profile']['first_name']
                    user.last_name = response['cyverse_profile']['last_name']
                    user.save()
                else:
                    print(f"No CyVerse profile")
        if request.user.profile.github_token != '' and user.profile.github_username != '':
            github_response = requests.get(f"https://api.github.com/users/{user.profile.github_username}",
                                           headers={'Authorization':
                                                        f"Bearer {request.user.profile.github_token}"})
            response['github_profile'] = github_response.json()
        return JsonResponse(response)

    @action(detail=False, methods=['get'])
    def get_key(self, request):
        overwrite = request.GET.get('overwrite', False)
        public_key = get_or_create_user_keypair(username=request.user.username, overwrite=overwrite)
        return JsonResponse({'public_key': public_key})

    @action(detail=False, methods=['get'])
    def start_dirt_migration(self, request):
        user = self.get_object()
        profile = Profile.objects.get(user=user)
        migration, created = Migration.objects.get_or_create(profile=profile)

        # connect to the DIRT DB
        db = Database(settings.DIRT_MIGRATION_DB_CONN_STR)
        async_to_sync(db.connect)()

        # make sure the user has a DIRT account
        email = request.query_params.get('email', None)

        # check for a DIRT CAS user with this user's username
        query = """SELECT * FROM cas_user WHERE cas_name = :cas_name"""
        row = async_to_sync(db.fetch_one)(query=query, values={"cas_name": user.username})

        # if we didn't find a CAS user and they provided an email, check that instead
        if row is None and email is not None:
            query = """SELECT * FROM users WHERE mail = :email"""
            row = async_to_sync(db.fetch_one)(query=query, values={"email": email})

            # if we can't find a DIRT user with the provided email address, abort the migration
            if row is None:
                async_to_sync(db.disconnect)()
                return HttpResponseBadRequest(f"Failed to find a DIRT user with CAS username '{user.username}' or email address '{email}'")

            # if we found a DIRT user matching the provided email address, save it and the associated name
            profile.dirt_email = email
            profile.dirt_name = row['name']
            profile.save()

        async_to_sync(db.disconnect)()

        # make sure a `dirt_migration` collection doesn't already exist
        client = TerrainClient(access_token=profile.cyverse_access_token)
        root_collection_path = f"/iplant/home/{user.username}/dirt_migration"
        if client.dir_exists(root_collection_path):
            self.logger.warning(f"Collection {root_collection_path} already exists, aborting DIRT migration for {user.username}")
            return HttpResponseBadRequest(f"DIRT migration collection already exists for {user.username}")

        # if already started, just return the migration status
        if not created and migration.started is not None:
            return JsonResponse({'migration': q.migration_to_dict(migration)})

        # record starting time
        start = timezone.now()
        migration.started = start
        migration.target_path = root_collection_path
        migration.downloads = json.dumps([])
        migration.uploads = json.dumps([])
        migration.save()
        profile.save()
        user.save()

        # submit migration task
        migrate_dirt_datasets.s(user.username).apply_async(countdown=5)

        # return status to client
        return JsonResponse({'migration': q.migration_to_dict(migration)})
