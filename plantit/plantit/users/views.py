from urllib.parse import parse_qs
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from github import Github
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_cas_ng.models import ProxyGrantingTicket

from plantit.users.serializers import UserSerializer
from plantit.util import csrf_token


class UsersViewSet(viewsets.ModelViewSet, mixins.RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    @action(detail=False, methods=['get'])
    def get_by_username(self, request):
        username = request.GET.get('username', None)
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
        if request.user.profile.cyverse_token is not '':
            cyverse_response = requests.get(f"https://de.cyverse.org/terrain/secured/user-info?username={user.username}", headers={'Authorization': f"Bearer {request.user.profile.cyverse_token}"})
            if cyverse_response.status_code == 401:
                response['cyverse_profile'] = 'expired token'
            else:
                response['cyverse_profile'] = cyverse_response.json()[user.username]
                user.first_name = response['cyverse_profile']['first_name']
                user.last_name = response['cyverse_profile']['last_name']
                user.save()
        if request.user.profile.github_token is not '':
            github_response = requests.get(f"https://api.github.com/users/{user.profile.github_username}", headers={'Authorization':
                                                     f"Bearer {request.user.profile.github_token}"})
            response['github_profile'] = github_response.json()
        return JsonResponse(response)

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

        return redirect('/workflows/')

    @action(methods=['get'], detail=False)
    def cyverse_cas_proxy_callback(self, request):
        token = ProxyGrantingTicket.retrieve_pt(request, 'https://de.cyverse.org/terrain')
        user = self.get_object()
        user.profile.cyverse_token = token
        user.save()

        return Response(status=200)
