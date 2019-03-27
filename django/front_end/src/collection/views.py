import os.path

from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView, FormView
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.mixins import LoginRequiredMixin

from plantit.job_manager.job import Status, Job
from .forms import CollectionFileForm, NewCollectionForm
from plantit.collection.models import Collection

from django import forms

class Details(LoginRequiredMixin,DetailView):
    """
        A view for showing the collection details.

        Attributes:
            template_name (str): The rendered template
                (default="workflows/collection/html/details.html")
            model (workflows.models.AbstractCollection): The type of model
                instance to crate. The model must extend the
                workflows.models.AbstractCollection class

        The class extends the django.views.generic.detail.DetailView class and
        also has all other attributes thereof.
    """
    template_name = "collection/collection.html"
    model = Collection

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] =  [t for t in self.object.tags.all()]
        context['metadata'] =  [m for m in self.object.metadata.all()]
        context['samples'] =  [f for f in self.object.sample_set.all()]
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.method == 'POST':
            if(request.POST['action'] == "delete"):
                self.remove_files(request)
        return self.get(request, *args, **kwargs)

    def remove_files(self,request):
        for pk in request.POST.getlist('pk'):
            self.object.samples.get(pk=pk).delete()

class List(LoginRequiredMixin,ListView):
    """
        A view for showing all collections for a given user or group

        Attributes:
            template_name (str): The rendered template
                (default="workflows/collection_list.html")
            model (workflows.models.AbstractCollection): The type of model
                instance to crate. The model must extend the
                workflows.models.AbstractCollection class

        The class extends the django.views.generic.list.ListView class and
        also has all other attributes thereof.
    """
    model = Collection
    template_name = "collection/collection_list.html"

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        delete_pk = request.GET.get('delete')
        if(delete_pk is not None):
            self.model.objects.get(pk = delete_pk).delete()

        return super(List,self).get(request, *args, **kwargs)

class New(LoginRequiredMixin,CreateView):
    """
        A form view for creating a new collection.

        Attributes:
            template_name (str): The rendered template
                (default="workflows/collection/html/new.html")
            model (workflows.models.AbstractCollection): The type of model
                instance to crate. The model must extend the
                workflows.models.AbstractCollection class

        The class extends the django.views.generic.edit.CreateView class and
        also has all other attributes thereof.
    """
    template_name = "collection/new.html"
    initial={
                'base_file_path': '/tempZone/home/rods/',
                'storage_type': 'irods'
            }

    # def get_initial(self):
    #     """
    #     Returns the initial data to use for forms on this view.
    #     """
    #     initial = super().get_initial()
    #
    #     initial['storage_type'] = 'cyverse'
    #     initial['base_file_path'] = '/iplant/home/' + str(self.request.user)
    #
    #     return initial

    def get_form(self):
        return NewCollectionForm(**self.get_form_kwargs())

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class EditDetails(LoginRequiredMixin,UpdateView):
    """
        A form view for editing the details of a collection

        Attributes:
            template_name (str): The rendered template
                (default="workflows/collection/html/edit_deatils.html")
            model (workflows.models.AbstractCollection): The type of model
                instance to crate. The model must extend the
                workflows.models.AbstractCollection class

        The class extends the django.views.generic.edit.UpdateView class and
        also has all other attributes thereof.
    """
    template_name = "collection/edit_details.html"
    model = Collection
    fields = ['name','description','tags','metadata']

class AddFiles(DetailView):
    """
        A view for adding/deleting files from the collection

        Attributes:
            template_name (str): The rendered template
                (default="workflows/collection/html/edit_files.html")
            model (workflows.models.AbstractCollection): The type of model
                instance to crate. The model must extend the
                workflows.models.AbstractCollection class
    """
    template_name = "collection/add_files.html"
    model = Collection

    def get_form(self, POST = None, FILES = None):
        return CollectionFileForm(storage_type=self.object.storage_type,
                           base_path=self.object.base_file_path,
                           data = POST,
                           files = FILES)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_form()
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.method == 'POST':
            form = self.get_form(POST = request.POST, FILES = request.FILES)
            if(form.is_valid()):
                files = form.cleaned_data['file']
                for file in files:
                    path = file.lstrip("/")
                    self.object.add_sample(path = path,
                                           name = os.path.basename(path))

        return HttpResponseRedirect(reverse('collection:details',args=[self.object.pk]))
