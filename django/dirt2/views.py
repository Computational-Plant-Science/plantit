from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from job_manager.job import Job

def index(request):
    """View function for home page of site."""

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'dirt2/index.html')

@login_required
def user_landing(request):
    """ User homepage """

    jobs = Job.objects.filter(user = request.user)

    context = {
        "jobs": jobs,
    }

    return render(request, 'dirt2/user_landing.html', context)
