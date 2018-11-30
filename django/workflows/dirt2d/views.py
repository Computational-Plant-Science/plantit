import workflows.views as views
from collection.models import Collection
from .forms import CreateJob
from . import logic

class Analyze(views.AnalyzeCollection):
    """
        Submits a job containing:
            + a :class:`job_manager.contrib.UploadFileTask` that uploads the
                root images in the collection to the cluster
            + a :class:`job_manager.contrib.SubmissionTask` that starts the
                analysis of the root images on the server
            + a :class:`job_mangaer.contrib.DownloadFileTask` that downloads
                the results of the analysis.
    """
    model = Collection
    form_class = CreateJob

    def submit(self,job, form):
        cluster = form.cleaned_data['cluster']

        logic.add_tasks(job,cluster,form.get_cleaned_attributes())

        super().submit(job,form)
