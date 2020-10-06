import json
import os
from urllib.parse import parse_qs
from urllib.parse import urlencode

from django.contrib.auth import login

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from github import Github
from requests.auth import HTTPBasicAuth
from rest_framework import viewsets, mixins
from rest_framework.decorators import action, authentication_classes
from rest_framework.permissions import AllowAny

from plantit.users.models import Profile
from plantit.users.serializers import UserSerializer
from plantit.util import csrf_token


class UsersViewSet(viewsets.ModelViewSet, mixins.RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        return self.request.user

    @action(detail=False, methods=['get'])
    @login_required
    def get_all(self, request):
        users = [{
            'username': 'Computational-Plant-Science',
            'github_username': 'Computational-Plant-Science'
        }, {
            'username': 'van-der-knaap-lab',
            'github_username': 'van-der-knaap-lab'
        }] + [{
            'username': user.username,
            'github_username': user.profile.github_username
        } for user in list(self.queryset)]
        return JsonResponse({
            'users': users
        })

    @action(detail=False, methods=['get'])
    def get_by_username(self, request):
        username = request.GET.get('username', None)

        # TODO move to configuration file
        if username == 'Computational-Plant-Science' or username == 'van-der-knaap-lab':
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

        user = self.queryset.get(username=username)
        response = {
            'django_profile': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }

        if request.user.username == user.username:
            response['django_profile']['cyverse_token'] = user.profile.cyverse_token

        if request.user.profile.cyverse_token != '':
            cyverse_response = requests.get(
                f"https://de.cyverse.org/terrain/secured/user-info?username={user.username}",
                headers={'Authorization': f"Bearer {request.user.profile.cyverse_token}"})
            if cyverse_response.status_code == 401:
                response['cyverse_profile'] = 'expired token'
            else:
                response['cyverse_profile'] = cyverse_response.json()[user.username]
                user.first_name = response['cyverse_profile']['first_name']
                user.last_name = response['cyverse_profile']['last_name']
                user.save()
        if request.user.profile.github_token != '':
            github_response = requests.get(f"https://api.github.com/users/{user.profile.github_username}",
                                           headers={'Authorization':
                                                        f"Bearer {request.user.profile.github_token}"})
            response['github_profile'] = github_response.json()
        return JsonResponse(response)

    @authentication_classes([AllowAny])
    @action(methods=['get'], detail=False)
    def cyverse_request_identity(self, request):
        session_state = request.GET.get('session_state', None)
        code = request.GET.get('code', None)
        response = requests.post("https://kc.cyverse.org/auth/realms/CyVerse/protocol/openid-connect/token", data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': os.environ.get('CYVERSE_REDIRECT_URL')})
        print(response.status_code)
        print(response.json())
        return HttpResponse(status=200)
        pass

    @authentication_classes([])
    @action(methods=['get'], detail=False)
    def cyverse_handle_temporary_code(self, request):
        session_state = request.GET.get('session_state', None)
        code = request.GET.get('code', None)

        if session_state is None:
            return HttpResponseBadRequest("Missing param: 'session_state'")
        if code is None:
            return HttpResponseBadRequest("Missing param: 'code'")

        response = requests.post("https://kc.cyverse.org/auth/realms/CyVerse/protocol/openid-connect/token", data={
            'grant_type': 'authorization_code',
            'client_id': 'local-testing',
            'code': code,
            'redirect_uri': os.environ.get('CYVERSE_REDIRECT_URL')}, auth=HTTPBasicAuth(request.user.username, '191a6ceb-931a-444d-b960-7982111b179f'))

        if response.status_code == 400:
            return HttpResponse('Unauthorized for KeyCloak token endpoint', status=401)

        if response.status_code != 200:
            return HttpResponse('Bad response from KeyCloak token endpoint', status=500)

        content = response.json()

        if 'access_token' not in content:
            return HttpResponseBadRequest("Missing param on token response: 'access_token'")

        token = content['access_token']
        print(token)

        import jwt
        import json
        decoded = jwt.decode(token, verify=False)
        print(json.dumps(decoded))

        user, created = User.objects.get_or_create(username=decoded['preferred_username'])

        user.first_name = decoded['given_name']
        user.last_name = decoded['family_name']
        user.email = decoded['email']
        user.save()

        if created:
            print('Created user: ' + user.username)
            profile = Profile.objects.create(user=user, cyverse_token=token)
        else:
            print('Retrieved user: ' + user.username)
            profile = Profile.objects.get(user=user)
            profile.cyverse_token = token

        profile.save()
        user.save()

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return redirect(f"/{user.username}/")

    @action(methods=['get'], detail=False)
    def github_request_identity(self, request):
        return redirect(settings.GITHUB_AUTH_URI + '?' + urlencode({
            'client_id': settings.GITHUB_KEY,
            'redirect_uri': settings.GITHUB_REDIRECT_URI,
            'state': csrf_token(request)}))

    @action(methods=['get'], detail=False)
    @authentication_classes([])
    def github_handle_temporary_code(self, request):
        state = request.GET.get('state', None)
        error = request.GET.get('error', None)
        if error == 'access_denied':
            return HttpResponseBadRequest()
        if state is None:
            return HttpResponseBadRequest()
        elif state != csrf_token(request):
            return HttpResponse('unauthorized', status=401)

        code = request.GET.get('code', None)
        if code is None:
            return HttpResponseBadRequest()

        response = requests.post('https://github.com/login/oauth/access_token', data={
            'client_id': settings.GITHUB_KEY,
            'client_secret': settings.GITHUB_SECRET,
            'redirect_uri': settings.GITHUB_REDIRECT_URI,
            'code': code})

        token = parse_qs(response.text)['access_token'][0]
        user = self.get_object()
        user.profile.github_username = Github(token).get_user().login
        user.profile.github_token = token
        user.profile.save()
        user.save()

        return redirect(f"/{user.username}/")
