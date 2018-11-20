import os
from .models import Defaults
from .tasks import DownloadResultsTask

from job_manager.remote import SubmissionTask, UploadCollectionTask, UploadFileTask
import json

def add_tasks(job,cluster,traits):
    '''
        Adds the tasks required to perform the analysis

        Args:
            job (:class:job_manager.job.Job): the job to add the tasks to
            cluster (:class:job_manager.remote.Cluster): cluster the job
                will be submitted to
            traits (dict): key: trait, value: true if to be calculated,
                false if to skip.
    '''
    defaults = Defaults.load()

    #Copy collection task
    copy_task = UploadCollectionTask(name="File Upload",
                  description="Upload files to cluster",
                  job=job,
                  cluster=cluster,
                  order_pos=1)
    copy_task.save()

    #Traits upload
    os.mkdir("files/tmp/" + job.work_dir)
    filename = "files/tmp/" + job.work_dir + "traits.csv"
    file = open(filename,"w")
    for key,value in traits.items():
        file.write(key + "," + str(int(value)) + "\n")
    traits_task = UploadFileTask(name = "Upload Traits",
        files = filename,
        delete=True,
        description="Upload traits to extract",
        job=job,
        cluster=cluster,
        order_pos=2)
    traits_task.save()

    #Submission task
    submit_task = SubmissionTask(name="Analysis",
                    description="Submits dirt2d Job",
                    submission_script=defaults.submission_script,
                    parameters=defaults.parameters,
                    order_pos=3,
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
                        order_pos=4)
    download_task.save()
