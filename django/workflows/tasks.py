import os
#import csv

from job_manager.job import Task,Status
from job_manager.remote import SSHTaskMixin

class DownloadResultsTask(SSHTaskMixin, Task):
    """
        Downloads and parsers output of a workflow.
    """
    output_filename = "results.csv"

    def ssh(self):
        _, file_extension = os.path.splitext(self.output_filename)
        output_file = self.workdir + "/" + self.output_filename
        file = self.sftp.file(output_file)

        self.job.results_file.save(
            "job%d%s"%(self.job.id,file_extension),
            file
        )

        #Cleanup
        self.finish()

# class ParseCSVMixin():
#     def parse(self, file):
#         """
#             Extracts the results from the csv file and inserts into a
#             results object using attributes attribute for field
#             mapping and value formatting.
#         """
#         reader = csv.DictReader(file, delimiter=',',restval=None)
#         collection = self.job.collection.cast()
#         for i,row in enumerate(reader):
#             if(i%2 == 0):#Skip the rows that are file headers
#                 image = collection.sample_set.get(name=row['Image name'])
#                 # try:
#                 #     image = collection.sample_set.get(name=row['Image name'])
#                 # except DoesNotExist as e:
#                 #     #TODO: Report this error to the job
#                 #     print("FILE DID NOT EXIST!!!!")
#                 #     continue
#
#                 result = self.result_class(job=self.job,sample=image)
#
#                 for key, value in row.items():
#                     if key in self.result_class.attributes:
#                         attr = self.result_class.attributes[key]['field']
#                         func = self.result_class.attributes[key]['type']
#                         setattr(result,
#                                 attr,
#                                 func(value))
#                 result.save()
