import csv

from job_manager.job import Task,Status
from job_manager.remote import SSHTaskMixin

from .models import Result

class DownloadResultsTask(SSHTaskMixin,Task):
    """
        Downloads and parsers the csv output by the DIRT algorithm. Populating
        RootImage objects with the resutls from each analyzed image.
    """

    def parse_csv_file(self,file):
        """
            Extracts the results from the csv file and inserts into the
            cooresponding RootImage object using attributs for field
            mapping and value formatting.
        """
        reader = csv.DictReader(file, delimiter=',',restval=None)
        collection = self.job.collection.cast()
        for i,row in enumerate(reader):
            if(i%2 == 0):#Skip the rows that are file headers
                image = collection.sample_set.get(name=row['Image name'])
                # try:
                #     image = collection.sample_set.get(name=row['Image name'])
                # except DoesNotExist as e:
                #     #TODO: Report this error to the job
                #     print("FILE DID NOT EXIST!!!!")
                #     continue

                result = Result(job=self.job,sample=image)

                for key, value in row.items():
                    if key in Result.attributes:
                        attr = Result.attributes[key]['field']
                        func = Result.attributes[key]['type']
                        setattr(result,
                                attr,
                                func(value))
                result.save()

    def ssh(self):
        output_file = self.workdir + "/calculated_traits.csv"
        file = self.sftp.file(output_file)
        self.parse_csv_file(file)

        #Cleanup
        self.finish()
