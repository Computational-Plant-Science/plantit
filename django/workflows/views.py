from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.urls import reverse

from job_manager.job import Status, Job
from collection.models import Collection

from workflows import registrar
from workflows.classes import Workflow

"""
    Views for analyzing :class:`collection.models.Collection`s.


"""
def list_workflows(request):
    """ List workflows """

    # Render the HTML template index.html with the data in the context variable
    context = {'workflows': registrar.list,
               'collection': request.GET['collection']}

    return render(request, 'workflows/choose_workflow.html', context)

class AnalyzeCollection(LoginRequiredMixin,SingleObjectMixin,FormView):
    """
        A form view for submiing a job to analzye the collection. When the
        form is submitted this view creates a new job and submits that job
        to the cluster by calling self.submit(job). Tasks can be added to a
        job prior to submitting it by exteding the class and overriding the
        submit() function.

        If an exception is thrown during the submit() call, the job is
        deleted and the expection reraised by the post() function.

        Example:
            from workflow import views

            class Analyze(views.AnalyzeCollection):

                ...

                def submit(self,job):
                    # Add tasks or or otheriwse modify job here
                    suer().submit(job)

        Requires:
            `model` attribute must be set by the extending class. The model
            should be the type collection model used by the workflow

            `form_class` attribute must be set by the extending class. This is
            the form shown by the view.

        Attributes:
            template_name (str): The rendered template
                (default="workflows/collection/analyze.html")
    """

    template_name = "workflows/analyze.html"
    model = Collection
    workflow = Workflow
    object = None

    def form_valid(self,form):
        collection = self.get_object()

        job = Job(collection = collection,
                  user = self.request.user)
        job.save()
        job.status_set.create(description="Created")

        try:
            self.submit(job,form)
            return HttpResponseRedirect(reverse("user:user_landing"))
        except Exception as e:
            job.delete()
            #TODO: Do something here to indicate to the user the job failed.
            raise e

    def submit(self, job, form):
        """
            Start the first task of the job.

            Args:
                job (class:`job_manager.models.Job`): The job that will be
                    submitted
                form: The filled and validated form, set by the form_class
                    class variable
        """
        cluster = form.cleaned_data['cluster']

        self.workflow.add_tasks(job, cluster, form)

        job.status_set.create(state=Status.OK,description="Submitted")
        Job.run_next(job.pk)
