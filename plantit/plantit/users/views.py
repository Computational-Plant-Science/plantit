import os
from urllib.parse import parse_qs
from urllib.parse import urlencode

import jwt
import requests
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from github import Github
from requests.auth import HTTPBasicAuth
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from plantit.users.models import Profile
from plantit.users.serializers import UserSerializer
from plantit.utils import csrf_token


class IDPViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

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

        if session_state is None:
            return HttpResponseBadRequest("Missing param: 'session_state'")
        if code is None:
            return HttpResponseBadRequest("Missing param: 'code'")

        response = requests.post("https://kc.cyverse.org/auth/realms/CyVerse/protocol/openid-connect/token", data={
            'grant_type': 'authorization_code',
            'client_id': os.environ.get('CYVERSE_CLIENT_ID'),
            'code': code,
            'redirect_uri': os.environ.get('CYVERSE_REDIRECT_URL')},
                                 auth=HTTPBasicAuth(request.user.username, os.environ.get('CYVERSE_CLIENT_SECRET')))

        if response.status_code == 400:
            return HttpResponse('Unauthorized for KeyCloak token endpoint', status=401)

        if response.status_code != 200:
            return HttpResponse('Bad response from KeyCloak token endpoint', status=500)

        content = response.json()

        if 'access_token' not in content:
            return HttpResponseBadRequest("Missing param on token response: 'access_token'")

        token = content['access_token']
        decoded = jwt.decode(token, options={
            'verify_signature': False,
            'verify_aud': False,
            'verify_iat': False,
            'verify_exp': False,
            'verify_iss': False
        })

        user, created = User.objects.get_or_create(username=decoded['preferred_username'])

        user.first_name = decoded['given_name']
        user.last_name = decoded['family_name']
        user.email = decoded['email']
        user.save()

        if created:
            profile = Profile.objects.create(user=user, cyverse_token=token)
        else:
            profile = Profile.objects.get(user=user)
            profile.cyverse_token = token

        profile.save()
        user.save()

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        # return redirect(f"/{user.username}/")
        return redirect("/")

    @action(methods=['get'], detail=False)
    def github_request_identity(self, request):
        return redirect(settings.GITHUB_AUTH_URI + '?' + urlencode({
            'client_id': settings.GITHUB_KEY,
            'redirect_uri': settings.GITHUB_REDIRECT_URI,
            'state': csrf_token(request)}))

    @action(methods=['get'], detail=False)
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


class UsersViewSet(viewsets.ModelViewSet, mixins.RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

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
    def get_all(self, request):
        # users = [{
        #     'username': 'Computational-Plant-Science',
        #     'github_username': 'Computational-Plant-Science'
        # }, {
        #     'username': 'van-der-knaap-lab',
        #     'github_username': 'van-der-knaap-lab'
        # }] +

        users = []
        for user in list(self.queryset):
            if user.profile.github_username:
                github_profile = requests.get(f"https://api.github.com/users/{user.profile.github_username}",
                                              headers={'Authorization':
                                                           f"Bearer {request.user.profile.github_token}"}).json()
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

        return JsonResponse({
            'users': users
        })

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

        user = self.queryset.get(username=username)
        response = {
            'django_profile': {
                'username': username,
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
