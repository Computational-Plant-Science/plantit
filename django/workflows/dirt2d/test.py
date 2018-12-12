from io import StringIO
import random
import string

from django.test import TestCase

from job_manager.test.test_models import create_user, create_job

from workflows.dirt2d.tasks import DownloadResultsTask
from workflows.dirt2d.models import Result
from collection.models import Collection


def create_root_collection():
    user = create_user()

    c = Collection.objects.create(name="TestCollection",
                                      description="Test files",
                                      user=user)
    c.save()

    c.sample_set.create(name='img1.png',
        path = 'files/tmp/img1.png')
    c.sample_set.create(name='img2.png',
        path = 'files/tmp/img2.png')
    c.sample_set.create(name='img3.png',
        path = 'files/tmp/img3.png')

    c.save()

    return c

class Dirt2DTests(TestCase):
    calculated_traits_csv="""Image ID,Image name,Failed,Experiment number,circle ratio,x pixel,y pixel,xScale,yScale,computation time,Skeleton Vertices,
1,img1.png,False,No label found,4,2,12,5.2,1.7,3,11,
Image ID,Image name,Failed,Experiment number,circle ratio,x pixel,y pixel,xScale,yScale,computation time,Skeleton Vertices,
1,img2.png,False,No label found,1,1,1,1.0,1.0,2,-1,
Image ID,Image name,Failed,Experiment number,circle ratio,x pixel,y pixel,xScale,yScale,computation time,Skeleton Vertices,
1,img3.png,False,No label found,2,4,4,1.5,1.22,7,12,
"""

    def test_parse_csv(self):
        c = create_root_collection()
        j = create_job(collection=c)

        task = DownloadResultsTask(job = j,name="Job");

        file = StringIO(self.calculated_traits_csv)

        task.parse_csv_file(file)

        samples = c.sample_set.all()
        img1 = Result.objects.get(job=j,sample=c.sample_set.get(name="img1.png"))
        img3 = Result.objects.get(job=j,sample=c.sample_set.get(name="img3.png"))

        #Check a few values
        self.assertEqual(img1.X_PIXEL,2)
        self.assertEqual(img1.SKL_NODES,11)
        self.assertEqual(img3.Y_SCALE,1.22)
        self.assertEqual(img3.COMP_TIME,7)
