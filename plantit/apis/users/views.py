from urllib.parse import parse_qs
from urllib.parse import urlencode

import requests
import yaml
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect
from github import Github, BadCredentialsException
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apis.users.serializers import UserSerializer
from apis.util import get_config, csrf_token


class ProfileViewSet(viewsets.ModelViewSet, mixins.RetrieveModelMixin):
    """
    API endpoint returning user info.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    with open("apis/users/countries.yaml", 'r') as f:
        _countries = yaml.safe_load(f)

    with open("apis/users/universities.yaml", 'r') as f:
        _universities = yaml.safe_load(f)

    def get_object(self):
        return self.request.user

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
        user.profile.github_auth_token = token
        user.save()

        return redirect('/workflows/')

    @action(methods=['get'], detail=False)
    def github_repos(self, request):
        user = self.get_object()
        token = user.profile.github_auth_token
        gh = Github(token)
        try:
            github_username = gh.get_user().login
        except BadCredentialsException:
            return Response([])

        response = requests.get(f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{github_username}", headers={"Authorization": f"token {token}"})
        pipelines = [{
            'repo': item['repository'],
            'config': get_config(item['repository'], token)
        } for item in response.json()['items']]
        return Response(pipelines)

    @action(methods=['get'], detail=False)
    def github_user(self, request):
        user = self.get_object()
        gh = Github(user.profile.github_auth_token)
        github_user = gh.get_user()
        try:
            return Response({
                'avatar_url': github_user.avatar_url
            })
        except BadCredentialsException:
            return Response([])

    @action(methods=['get'], detail=False)
    def countries(self, request):
        return Response({
            'countries': self._countries
        })

    @action(methods=['get'], detail=False)
    def universities(self, request):
        country = request.GET.get('country', None)
        if country in self._universities:
            return Response({
                'universities': self._universities[country]
            })
        else:
            return HttpResponseNotFound()
