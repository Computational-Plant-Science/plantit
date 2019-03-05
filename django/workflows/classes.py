import json

from job_manager.remote import UploadCollectionTask, SubmissionTask
from .tasks import DownloadResultsTask

class Workflow:

    @classmethod
    def add_tasks(cls,job,cluster,form,app_name):
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
                        parameters=json.dumps(form.get_grouped_data(), default= lambda o: str(o)),
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
