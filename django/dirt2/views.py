from django.shortcuts import render
from django.contrib.auth import logout
from django.http.response import HttpResponseRedirect
from django.urls import reverse

def index(request):
    """View function for home page of site."""

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'dirt2/index.html')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))
