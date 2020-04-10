"""
    Methods for submitting workflow jobs.
"""
import json
from ..job_manager.remote import UploadCollectionTask, SubmissionTask
from ..job_manager.job import Cluster
from ..collection.models import Collection
from ..job_manager.job import Job, Status


def default_params():
    """
        Generates the user configurable parameters required by Plant IT
        that are general to all workflow submissions

        Returns:
            A dictionary of default parameters in the cookiecutter
            Plant IT workflow parameter format.
    """
    clusters = Cluster.objects.all()

    param_group = {
        "id": "submission_settings",
        "name": "Submission Settings",
        "params": [{
            "id": "cluster",
            "type": "select",
            "initial": clusters.first().name if clusters.count() is not 0 else "",
            "options": [cluster.name for cluster in clusters],
            "name": "Cluster",
            "description": "Compute cluster to run the analysis on."
        }]
    }

    return param_group


def add_tasks(job, cluster, params, app_name):
    """
        Populates the given job with the tasks required to submit a workflow job
        to the a cluster to perform the analysis.

        Args:
            job (:class:`plantit.job_manager.job.Job`): the job to add the tasks to
            cluster (:class:`plantit.job_manager.remote.Cluster`): cluster the job
                will be submitted to
            params (dict): workflow user-configurable parameters in the
                format accepted by the Plant IT cookiecutter process function.
                (i.e. params are passed into process as the args variable).
            app_name:

    """

    # Copy collection task
    copy_task = UploadCollectionTask(name="File Upload",
                                     description="Upload files to cluster",
                                     job=job,
                                     cluster=cluster,
                                     order_pos=10)
    copy_task.save()

    # Submission task
    submit_task = SubmissionTask(name="Analysis",
                                 description="Starts the analysis on the cluster",
                                 app_name=app_name,
                                 parameters=json.dumps(params),
                                 order_pos=20,
                                 job=job,
                                 cluster=cluster)
    submit_task.save()


def submit(user, workflow, collection_pk, params):
    """
        Submit a workflow for analysis.

        Creates a :class:`plantit.job_manager.job.Job`, populates it with tasks to
        apply the given workflow to the given collection and starts the job.

        Args:
            user (:class:`django.contrib.auth.models.User`): django user doing the analysis
            workflow (str): app_name of workflow
            collection_pk (int): pk of collection to analyze
            params (dict): workflow user-configurable parameters in the
                format accepted by the Plant IT cookiecutter process function.
                (i.e. params are passed into process as the args variable).
    """

    cluster = Cluster.objects.get(name=params['submission_settings']['params']['cluster'])
    collection = Collection.objects.get(pk=collection_pk)

    job = Job(collection=collection,
              user=user,
              workflow=workflow,
              cluster=cluster)
    job.save()
    job.status_set.create(description="Created")

    try:
        add_tasks(job, cluster, params, workflow)
        job.status_set.create(state=Status.OK, description="Submitted")
        Job.run_next(job.pk)
    except Exception as e:
        job.delete()
        # TODO: Do something here to indicate to the user the job failed.
        raise e

    return job.pk
