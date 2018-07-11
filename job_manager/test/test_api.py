import json

from django.test import TestCase
from rest_framework.test import APITestCase

from job_manager.test.test_models import create_job, add_task
# Using the standard RequestFactory API to create a form POST request

class TestAPI(APITestCase):
    def setUp(self):
        self.url = '/jobs/api'

    def test_authorization_needed(self):
        """
            Test that requests without authorization are denied with
                HTML code "401 Unauthorized"
        """
        response = self.client.get(self.url + '/jobs/')
        self.assertEqual(401, response.status_code)

    def test_get_job(self):
        """
            Test getting job
        """
        j = create_job()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + j.auth_token)
        response = self.client.get(self.url + '/jobs/' + str(j.pk) + '/')
        response_data = json.loads(response.content)

        self.assertEqual(200,response.status_code)
        self.assertEqual(j.pk,response_data.get("pk"))

    def test_set_status(self):
        """
         Test updating a job's status
        """
        j = create_job()
        e = add_task(j)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + j.auth_token)
        packet = {"submission_id" : "",
                   "status_set" : [
                        {
                        "state" : 1,
                        "date" : "2018-06-27T16:28:22.931941-04:00",
                        "description" : "Status Set"
                        }
                    ]
                }
        response = self.client.patch(self.url + '/jobs/' + str(j.pk) + '/',packet, format='json')
        response_data = json.loads(response.content)
        self.assertEqual(200,response.status_code)
        self.assertEqual("Status Set",response_data['status_set'][0]['description'])
        self.assertEqual(1,response_data['task_set'][0]['pk'])

    def test_set_submission_id(self):
        """
            Test setting the submission id for a job
        """
        j = create_job()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + j.auth_token)
        packet = {"submission_id" : 55,
                   "status_set" : []
                 }
        response = self.client.patch(self.url + '/jobs/' + str(j.pk) + '/',packet, format='json')
        response_data = json.loads(response.content)
        self.assertEqual(200,response.status_code)
        self.assertEqual('55',response_data['submission_id'])

    def test_set_task_state(self):
        """
            Test setting a job task to complete
        """
        j = create_job()
        t = add_task(j)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + j.auth_token)
        packet = {"submission_id" : 55,
                   "task_set" : [{
                    "pk": t.pk,
                    "complete": True
                    }
                   ]
                 }
        response = self.client.patch(self.url + '/jobs/' + str(j.pk) + '/',packet, format='json')
        response_data = json.loads(response.content)
        self.assertEqual(200,response.status_code)
        self.assertEqual(t.pk,response_data['task_set'][0]['pk'])
        self.assertEqual(True,response_data['task_set'][0]['complete'])
