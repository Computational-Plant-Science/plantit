import json
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect

def login_view(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)

        try:
            username = json_data['username']
        except KeyError:
            return HttpResponse("Username required")

        try:
            password = json_data['password']
        except KeyError:
            return HttpResponse("Password required")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponse("OK")

        return HttpResponse("FAILED")
    else:
        return HttpResponse("FAILED")

def logout_view(request):
    logout(request)
    return redirect('/')
