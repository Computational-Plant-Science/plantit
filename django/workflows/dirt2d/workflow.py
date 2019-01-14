import os

from workflows.classes import Workflow
from workflows import registrar

from job_manager.remote import UploadFileTask

from .models import DownloadDirt2DResults

name = "DIRT"
description = "Digital imaging of root traits (DIRT) measures traits of monocot and dicot roots from digital images. DIRT automates the extraction of root traits by making high-throughput grid computing environment available to end-users without technical training."
icon_loc = "workflows/dirt2d/icon.png"
registrar.register(name,description,"dirt2d",icon_loc)

class Workflow(Workflow):
    results_task = DownloadDirt2DResults
    singularity_url = "shub://cottersci/DIRT2_Workflows:dirt2d"

    @classmethod
    def get_singularity_params(cls,form):
        params = [
                    "--threshold=" + str(form.cleaned_data['threshold']),
                    "--in=files/*",
                    "--traits={pwd}/traits.csv"
                 ]
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
        super().add_tasks(job,cluster,form)

        traits = form.get_cleaned_attributes()

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
            order_pos=1)
        traits_task.save()
