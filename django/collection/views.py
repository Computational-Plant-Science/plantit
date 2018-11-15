from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView, FormView
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.mixins import LoginRequiredMixin

from job_manager.job import Status, Job
from .forms import CollectionFileForm, NewCollectionForm
from .images import Images2D, Image

from django import forms

# class FilesObjectMixin():
#     """
#         Defines the stradgey for accessing the ForeignKey field in the
#         collection object that contains the files. By default, this field is
#         named "files" and all objects within the filed should be included.
#         These defaults can changed by overriding the :meth:`get_files` and
#         :meth:`get_files_object` methods.
#     """
#     def get_files(self):
#         """
#             Get the files within the collection.
#
#             Returns:
#                 A queryselect object containing the files within this collection
#         """
#         return self.get_files_object().all().values()
#
#     def get_files_object(self):
#         """
#             Get the collection field containing the files
#
#             Returns:
#                 object of the field that contains the collection files
#         """
#         return self.object.files

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
    template_name = "collection/html/collection.html"
    model = Images2D

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] =  [t for t in self.object.tags.all()]
        context['metadata'] =  [m for m in self.object.metadata.all()]
        context['files'] =  [f for f in self.object.files.all()]
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.method == 'POST':
            if(request.POST['action'] == "delete"):
                self.remove_files(request)
        return self.get(request, *args, **kwargs)

    def remove_files(self,request):
        for pk in request.POST.getlist('pk'):
            self.object.files.get(pk=pk).delete()

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
    model = Images2D
    template_name = "collection/html/collection_list.html"

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
    template_name = "collection/html/new.html"
    initial={'base_file_path': 'files/'}

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
    template_name = "collection/html/edit_details.html"
    model = Images2D
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
    template_name = "collection/html/add_files.html"
    model = Images2D

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
                    self.object.add_file(file)

        return self.get(request, *args, **kwargs)
