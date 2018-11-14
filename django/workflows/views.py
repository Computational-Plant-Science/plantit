from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.http.response import HttpResponseRedirect

from .forms import CreateJob

from job_manager.job import Status, Job



"""
    Views for viewing, editing, and analyzing a :class:`workflows.models.AbstractCollection`.

    The classes should be extended by a workflow to define the
    collection model. See :module:`workflows.dirt2d` for a full example.

    A typical set of views and urls for a workflow:

    ============================   ======================  =======================
    Relative Path                  Class                   Description
    ============================   ======================  =======================
                                   ListView                List of collections
    collection/new/,               NewCollection           Create a new collection
    collection/<pk>/files/         CollectionFilesView     Show collection files
    collection/<pk>/details/       CollectionDetailView    Show collection details
    collection/<pk>/analyze/       AnalyzeCollection       Analyze the collection
    collection/<pk>/edit/images    EditCollectionFiles     Add/Delete files
    collection/<pk>/edit/details   EditCollectionDetails   Edit collection details
    ============================   ======================  =======================

    models.py:
    .. code-block:: python
        from workflows.models import AbstractCollection

        ...

        class Collection(AbstractCollection)
            ...

    views.py
    .. code-block:: python
        import workflows.views as views
        from .models import Collection

        ...

        class New(views.NewCollection):
            model = Collection

        class ListView(views.CollectionListView):
            model = Collection

        # and so on for CollectionDetailView, EditCollectionView, EditCollectionFiles,
        #   and AnalyzeCollection.

    urls.py:
    .. code-bock:: python
        import .views as views

        ...

        urlpatterns = [
            path('',views.ListView.as_view()),
            path('collection/new/', views.New.as_view(), name="new"),
            path('collection/<pk>/files/',views.CollectionFileView.as_view(), name="images"),
            path('collection/<pk>/details/',views.CollectionDetailView.as_view(), name="details"),
            path('collection/<pk>/analyze/',views.AnalyzeCollection.as_view(), name="analyze"),
            path('collection/<pk>/edit/images',views.EditCollectionFiles.as_view(), name="edit_images"),
            path('collection/<pk>/edit/details',views.EditCollectionDetails.as_view(),name="edit_details")
        ]

        # Replacing the view class names in the above example with the extended
        # views from the workflow.

    Some views have other methods or attributes that may be useful to change
    in the exteded class. See each class for details.
"""
from workflows import registrar

def list_workflows(request):
    """View function for home page of site."""

    # Render the HTML template index.html with the data in the context variable
    context = {'workflows': registrar.list,
               'collection': request.GET['collection']}

    return render(request, 'workflows/html/list_workflows.html', context)

class AnalyzeCollection(LoginRequiredMixin,DetailView):
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
            The model attribute must be set by the extending class

        Attributes:
            template_name (str): The rendered template
                (default="workflows/collection/analyze.html")
            model (workflows.models.AbstractCollection): The type of model
                instance to crate. The model must extend the
                workflows.models.AbstractCollection class
    """

    template_name = "workflows/html/analyze.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = CreateJob
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CreateJob(request.POST)
        form.instance.user = request.user
        form.instance.collection = self.object
        job = form.save()
        job.status_set.create(description="Created")
        try:
            self.submit(job,form)
            return HttpResponseRedirect(reverse("user_landing"))
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
        """
        job.status_set.create(state=Status.OK,description="Submitted")
        Job.run_next(job.pk)
