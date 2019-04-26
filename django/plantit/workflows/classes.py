import json

from ..job_manager.remote import UploadCollectionTask, SubmissionTask, Cluster
from .tasks import DownloadResultsTask
from ..collection.models import Collection
from ..job_manager.job import Job, Status

class Workflow:
    @classmethod
    def default_params(cls):
        clusters = Cluster.objects.all()

        param_group = {
            "id": "submission_settings",
            "name": "Submission Settings",
            "params": [{
                "id": "cluster",
                "type": "select",
                "initial": clusters.first().name,
                "options": [cluster.name for cluster in clusters],
                "name": "Cluster",
                "description": "Compute cluster to run the analysis on."
            }]
        }

        return param_group

    @classmethod
    def add_tasks(cls,job,cluster,params,app_name):
        '''
            Adds the tasks required to perform the analysis

            Args:
                job (:class:job_manager.job.Job): the job to add the tasks to
                cluster (:class:job_manager.remote.Cluster): cluster the job
                    will be submitted to
                traits (dict): key: trait, value: true if to be calculated,
                    false if to skip.
        '''

        #Copy collection task
        copy_task = UploadCollectionTask(name="File Upload",
                      description="Upload files to cluster",
                      job=job,
                      cluster=cluster,
                      order_pos=10)
        copy_task.save()

        #Submission task
        submit_task = SubmissionTask(name="Analysis",
                        description="Starts the analysis on the cluster",
                        app_name=app_name,
                        parameters=json.dumps(params),
                        order_pos=20,
                        job=job,
                        cluster=cluster)
        submit_task.save()

        #Results task
        download_task = DownloadResultsTask(name="Download Results",
                            description="Downloads and parses results",
                            job=job,
                            cluster=cluster,
                            order_pos=30)
        download_task.save()


    @classmethod
    def submit(cls,user,workflow,collection_pk,params):
        '''
            Submit a workflow for analysis

            Args:
                user: django user doing the analysis
                workflow (str): app_name of workflow
                collection_pk (int): pk of collection to analyze
                params (dict): workflow parameter settings
        '''

        cluster = Cluster.objects.get(name = params['submission_settings']['params']['cluster'])
        collection = Collection.objects.get(pk = collection_pk)

        job = Job(collection = collection,
                  user = user)
        job.save()
        job.status_set.create(description="Created")

        try:
            cls.add_tasks(job, cluster, params, workflow)
            job.status_set.create(state=Status.OK,description="Submitted")
            Job.run_next(job.pk)
        except Exception as e:
            job.delete()
            #TODO: Do something here to indicate to the user the job failed.
            raise e

        return job.pk
