from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CollectionFileForm, CreateJob

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

class FilesObjectMixin():
    """
        Defines the stradgey for accessing the ForeignKey field in the
        collection object that contains the files. By default, this field is
        named "files" and all objects within the filed should be included.
        These defaults can changed by overriding the :meth:`get_files` and
        :meth:`get_files_object` methods.
    """
    def get_files(self):
        """
            Get the files within the collection.

            Returns:
                A queryselect object containing the files within this collection
        """
        return self.get_files_object().all().values()

    def get_files_object(self):
        """
            Get the collection field containing the files

            Returns:
                object of the field that contains the collection files
        """
        return self.object.files

class CollectionDetailView(LoginRequiredMixin,DetailView):
    """
        A view for showing the collection details.

        Requires:
            The model attribute must be set by extending the class

        Attributes:
            template_name (str): The rendered template
                (default="workflows/collection/details.html")
            model (workflows.models.AbstractCollection): The type of model
                instance to crate. The model must extend the
                workflows.models.AbstractCollection class

        The class extends the django.views.generic.detail.DetailView class and
        also has all other attributes thereof.
    """
    template_name = "workflows/collection/details.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] =  [t for t in self.object.tags.all()]
        context['metadata'] =  [m for m in self.object.metadata.all()]
        return context

class CollectionFileView(LoginRequiredMixin,DetailView, FilesObjectMixin):
    """
        A view for showing all files within the collection.

        Mixins:
            + class:`FilesObjectMixin`

        Requires:
            The model attribute must be set by extending the class

        Attributes:
            template_name (str): The rendered template
                (default="workflows/collection/files.html")
            model (workflows.models.AbstractCollection): The type of model
                instance to crate. The model must extend the
                workflows.models.AbstractCollection class

        The class extends the django.views.generic.detail.DetailView class and
        also has all other attributes thereof.
    """
    template_name = "workflows/collection/files.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['files'] =  [f for f in self.get_files()]
        return context

class CollectionListView(LoginRequiredMixin,ListView):
    """
        A view for showing all collections of the model type

        Requires:
            The model attribute must be set by extending the class

        Attributes:
            template_name (str): The rendered template
                (default="workflows/collection_list.html")
            model (workflows.models.AbstractCollection): The type of model
                instance to crate. The model must extend the
                workflows.models.AbstractCollection class

        The class extends the django.views.generic.list.ListView class and
        also has all other attributes thereof.
    """
    template_name = "workflows/collection_list.html"

class NewCollection(LoginRequiredMixin,CreateView):
    """
        A form view for creating a new collection.

        Requires:
            The model attribute must be set by extending the class

        Attributes:
            template_name (str): The rendered template
                (default="workflows/collection/new.html")
            model (workflows.models.AbstractCollection): The type of model
                instance to crate. The model must extend the
                workflows.models.AbstractCollection class

        The class extends the django.views.generic.edit.CreateView class and
        also has all other attributes thereof.
    """
    template_name = "workflows/collection/new.html"
    fields = ['name','description','tags','metadata']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class EditCollectionDetails(LoginRequiredMixin,UpdateView):
    """
        A form view for editing the details of a collection

        Requires:
            The model attribute must be set by the extending class

        Attributes:
            template_name (str): The rendered template
                (default="workflows/collection/edit_deatils.html")
            model (workflows.models.AbstractCollection): The type of model
                instance to crate. The model must extend the
                workflows.models.AbstractCollection class

        The class extends the django.views.generic.edit.UpdateView class and
        also has all other attributes thereof.
    """
    template_name = "workflows/collection/edit_details.html"
    fields = ['name','description','tags','metadata']

class EditCollectionFiles(LoginRequiredMixin,DetailView, FilesObjectMixin):
    """
        A form view for adding/deleting files from the collection

        Mixins:
            + class:`FilesObjectMixin`

        Requires:
            The model attribute must be set by the extending class

        Attributes:
            template_name (str): The rendered template
                (default="workflows/collection/edit_files.html")
            model (workflows.models.AbstractCollection): The type of model
                instance to crate. The model must extend the
                workflows.models.AbstractCollection class
    """
    template_name = "workflows/collection/edit_files.html"
    form_class = CollectionFileForm

    def get_form(self, POST = None, FILES = None):
        return self.form_class(choices = self.get_files(), data=POST, files=FILES)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_form()
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        files_object = self.get_files_object()
        if request.method == 'POST':
            form = self.get_form(POST = request.POST, FILES = request.FILES)
            if(form.is_valid()):
                if(form.cleaned_data['file']):
                    file = form.cleaned_data['file']
                    storage = FileSystemStorage('')
                    name = str(file)
                    path = 'files/' + name
                    storage.save(path,file)
                    files_object.create(path=path,name=name)
                elif(form.cleaned_data['files']):
                    for name in form.cleaned_data['files']:
                        storage = FileSystemStorage('')
                        img = files_object.get(name=name)
                        storage.delete(img.path)
                        files_object.get(name=name).delete()
        return self.get(request, *args, **kwargs)

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

    template_name = "workflows/collection/analyze.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if(not self.object.job):
            form = CreateJob
            context['form'] = form
        else:
            context['job'] = self.object.job
            context['status'] = [s for s in self.object.job.status_set.all()]
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CreateJob(request.POST)
        form.instance.user = request.user
        job = form.save()
        job.status_set.create(description="Created")
        try:
            self.submit(job,form)
        except Exception as e:
            job.delete()
            #Do something here to indicate to the user the job failed.
            raise e
        self.object.job = job
        self.object.save()
        return self.get(request, *args, **kwargs)

    def submit(self, job, form):
        """
            Start the first task of the job.

            Args:
                job (class:`job_manager.models.Job`): The job that will be
                    submitted
        """
        job.status_set.create(state=Status.OK,description="Submitted")
        Job.run_next(job.pk)
