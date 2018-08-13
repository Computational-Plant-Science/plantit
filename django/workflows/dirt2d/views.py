import workflows.views as views
import workflows.forms as forms

from .models import RootCollection, Defaults
from .tasks import DownloadResultsTask

from job_manager.remote import SubmissionTask, UploadFileTask

"""
    View urls
    ---------

    ============================   ==============
    Relative Path                  Class
    ============================   ==============
    /                              ListView
    collection/new/,               New
    collection/<pk>/images/        ImageView
    collection/<pk>/details/       DetailView
    collection/<pk>/analyze/       Analyze
    collection/<pk>/edit/images    EditFiles
    collection/<pk>/edit/details   EditDetails
    ============================   ==============
"""

class New(views.NewCollection):
    model = RootCollection

class ListView(views.CollectionListView):
    model = RootCollection

class ImageView(views.CollectionFileView):
    model = RootCollection

    def get_files_object(self):
        return self.object.images

class DetailView(views.CollectionDetailView):
    model = RootCollection

class EditDetails(views.EditCollectionDetails):
    model = RootCollection

class EditFiles(views.EditCollectionFiles):
    model = RootCollection

    def get_files_object(self):
        return self.object.images

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
    model = RootCollection

    def submit(self,job, form):
        defaults = Defaults.load()
        cluster = form.cleaned_data['cluster']

        #Copy image task
        copy_task = UploadFileTask(name="File Upload",
                    description="Uploades files to cluster",
                    backend='FileSystemStorage',
                    pwd='',
                    files=','.join([img.path for img in self.object.images.all()]),
                    job=job,
                    cluster=cluster)
        copy_task.save()

        #Submission task
        submit_task = SubmissionTask(name="Analysis",
                        description="Submits dirt2d Job",
                        submission_script=defaults.submission_script,
                        parameters=defaults.parameters,
                        order_pos=2,
                        job=job,
                        cluster=cluster)
        submit_task.save()
        try:
            for f in defaults.files.all():
                submit_task.files.add(f)
        except Error as e:
            submit_task.delete()
            raise e

        #Results task
        download_task = DownloadResultsTask(name="Download Results",
                            description="Downloads and parses results",
                            job=job,
                            cluster=cluster,
                            order_pos=3)
        download_task.save()

        super().submit(job,form)
