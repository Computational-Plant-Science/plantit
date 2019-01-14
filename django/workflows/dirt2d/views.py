from django.http.response import HttpResponse

import workflows.views as views
from collection.models import Collection

from .forms import CreateJob
from . import logic
from .workflow import Workflow

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
    workflow = Workflow
    form_class = CreateJob

def segment_image(request,pk):
    collection = Collection.objects.get(pk = pk)
    image_obj = collection.sample_set.first()
    threshold = float(request.GET['threshold'])

    file = image_obj.get(request.user,collection.base_file_path)

    segmented = logic.segment(file,threshold)

    return HttpResponse(segmented.getvalue(), content_type="image/jpeg")
