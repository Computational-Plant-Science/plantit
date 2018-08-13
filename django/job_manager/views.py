from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .job import Job

# Create your views here.
@login_required
def job_list(request):
    jobs = Job.objects.all()

    current_status = []
    for j in jobs:
        j.status = j.current_status()

    context = { 'jobs':jobs }

    return render(request, 'job_manager/job_list.html', context)

@login_required
def submit_job(request, job_pk):
    Job.run_next(job_pk)

    return HttpResponseRedirect(reverse('job_manager:job_list'))
