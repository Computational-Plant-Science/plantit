import json

from .models import Result
from job_manager.remote import UploadCollectionTask, SubmissionTask

class Workflow:
    results_task = None

    @classmethod
    def get_singularity_params(cls,form):
        """
            The parameters to pass to the singularity container.

            Returns:
                a list of parameters to add to to the call to the singularity
                container
        """
        params = []
        for key, val in form.cleaned_data.items():
            params.extend([str(key), str(val)])

        return params

    @classmethod
    def add_tasks(cls,job,cluster,form):
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
                        parameters=json.dumps(cls.get_singularity_params(form)),
                        order_pos=20,
                        job=job,
                        cluster=cluster,
                        singularity_url=cls.singularity_url)
        submit_task.save()

        #Results task
        download_task = cls.results_task(name="Download Results",
                            description="Downloads and parses results",
                            job=job,
                            cluster=cluster,
                            order_pos=30)
        download_task.save()