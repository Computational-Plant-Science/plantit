from django.test import TestCase

from job_manager import tasks
from job_manager.test.test_models import create_cluster, create_executor, create_job
from job_manager.models import Status

class TasksTests(TestCase):
    def test_submit_job(self):
        """
            Test submitting job to cluster
        """
        e = create_executor()
        c = create_cluster()
        j = create_job(cluster=c, executor=e)
        try:
            tasks.__submit_job__(pk=j.pk)
        except:
            self.assertIs(False,True)

    def test_login_failed(self):
        """
            Test that job state is set to FAILED if server login fails
        """
        e = create_executor()
        c = create_cluster(uname="hacker")
        j = create_job(cluster=c, executor=e)
        tasks.__submit_job__(pk=j.pk)
        self.assertIs(j.current_status().state == Status.FAILED,True)

    def test_submit_failed(self):
        """
            Test job state is set to FAILED if the server scripts return
            and error code
        """
        e = create_executor()
        c = create_cluster(submit_commands="cat a_file_that_does_not_exist.sh")
        j = create_job(cluster=c, executor=e)
        tasks.__submit_job__(pk=j.pk)
        self.assertIs(j.current_status().state == Status.FAILED,True)

    def test_cancel_unsubmitted_job(self):
        """
            Test that a canceled job that was not sumbitted to the cluster
            is has a state of FAILED
        """
        j = create_job()
        tasks.__cancel_job__(pk=j.pk)
        self.assertIs(j.current_status().state == Status.FAILED,True)

    def test_cancel_submitted_job(self):
        pass

    def test_cancel_failed(self):
        pass
