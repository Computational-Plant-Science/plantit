import json
from random import choice
from urllib.parse import parse_qs
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect
from github import Github
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apis.user.serializers import UserSerializer


class ProfileViewSet(viewsets.ModelViewSet, mixins.RetrieveModelMixin):
    """
    API endpoint returning user info.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

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

        return redirect('/dashboard/')

    @action(methods=['get'], detail=False)
    def github_repos(self, request):
        user = self.get_object()
        gh = Github(user.profile.github_auth_token)
        github_username = gh.get_user().login

        response = requests.get(f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{github_username}")
        hits = response.json()['items']
        repos = [hit['repository'] for hit in hits]

        return Response(repos)

        # code_hits = gh.search_code(query=f"filename:plantit.yaml+user:{gh.get_user().login}")
        # repos = [code.repo]
        #return Response([{
        #    'name': repo.name,
        #    'description': repo.description,
        #    'url': repo.url,
        #    'stars': repo.stargazers_count
        #} for repo in repos])


def csrf_token(request):
    token = request.session.get('csrfToken', None)
    if token is None:
        token = secret_key()
        request.session['csrfToken'] = token
    return token


def random_string(length, allowed_chars='abcdefghijklmnopqrstuvwxyz' 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    return ''.join(choice(allowed_chars) for i in range(length))


def secret_key():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return random_string(40, chars)
