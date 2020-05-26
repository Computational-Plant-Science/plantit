"""
    Methods for submitting workflow jobs.
"""
import json
import os

from plantit.collection.models import Collection
from plantit.jobs.models.cluster import Cluster
from plantit.jobs.models.job import Job
from plantit.jobs.models.status import Status
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def default_params():
    """
        Generates the user configurable parameters required by Plant IT
        that are general to all workflow submissions

        Returns:
            A dictionary of default parameters in the cookiecutter
            Plant IT workflow parameter format.
    """
    clusters = Cluster.objects.all()

    param_group = {
        "id": "submission_settings",
        "name": "Submission Settings",
        "params": [{
            "id": "cluster",
            "type": "select",
            "initial": clusters.first().name if clusters.count() is not 0 else "",
            "options": [cluster.name for cluster in clusters],
            "name": "Cluster",
            "description": "Compute cluster to run the analysis on."
        }]
    }

    return param_group


def submit(user, workflow, collection_pk, params):
    """
        Submit a workflow for analysis.

        Creates a :class:`plantit.job_manager.job.Job`, populates it with tasks to
        apply the given workflow to the given collection and starts the job.

        Args:
            user (django.contrib.auth.models.User): django user doing the analysis
            workflow (str): app_name of workflow
            collection_pk (int): pk of collection to analyze
            params (dict): workflow user-configurable parameters in the
                format accepted by the Plant IT cookiecutter process function.
                (i.e. params are passed into process as the args variable).
    """

    cluster = Cluster.objects.get(name=params['submission_settings']['params']['cluster'])
    collection = Collection.objects.get(pk=collection_pk)

    job = Job(collection=collection,
              user=user,
              workflow=workflow,
              cluster=cluster,
              parameters=json.dumps(params))
    print(f"token: {job.token}")
    print(f"work_dir: {job.work_dir}")
    job.save()
    job.status_set.create(description="Created")

    try:
        client = Client(
            transport=RequestsHTTPTransport(
                url=os.environ['DAGIT_GRAPHQL_URL'],
                verify=False,
                retries=3,
            ),
            fetch_schema_from_transport=True,
        )

        query = gql('''
            mutation ($executionParams: ExecutionParams!) {
              startPipelineExecution(executionParams: $executionParams) {
                ...startPipelineExecutionResultFragment
              }
            }

            fragment startPipelineExecutionResultFragment on StartPipelineExecutionResult {
              __typename
              ... on InvalidStepError {
                invalidStepKey
              }
              ... on InvalidOutputError {
                stepKey
                invalidOutputName
              }
              ... on PipelineConfigValidationInvalid {
                pipelineName
                errors {
                  __typename
                  message
                  path
                  reason
                }
              }
              ... on PipelineNotFoundError {
                message
                pipelineName
              }
              ... on PythonError {
                message
                stack
              }
              ... on StartPipelineRunSuccess {
                run {
                  runId
                  status
                  pipeline {
                    name
                  }
                  environmentConfigYaml
                  mode
                }
              }
              ... on PipelineRunConflict {
                message
              }
            }
        ''')
        params = {
            "executionParams": {
                "selector": {
                    "name": "workflow"
                },
                "mode": "default",
                "environmentConfigData": {
                    "execution": {
                        "celery": {
                            "config": {
                                "backend": "amqp://rabbitmq",
                                "broker": "amqp://rabbitmq"
                            }
                        }
                    },
                    "storage": {
                        "filesystem": {
                            "config": {
                                "base_dir": "/opt/dagster"
                            }
                        }
                    },
                    "solids": {
                        "create_directory": {
                            "inputs": {
                                "job": {
                                    "pk": job.pk,
                                    "collection": {
                                        "name": collection.name,
                                        "storage_type": collection.storage_type,
                                        "base_file_path": collection.base_file_path,
                                        "sample_set": json.loads(collection.to_json())['sample_set']
                                    },
                                    "workflow": workflow,
                                    "work_dir": job.work_dir,
                                    "remote_results_path": job.remote_results_path,
                                    "cluster": {
                                        "name": cluster.name,
                                        "username": cluster.username,
                                        "password": cluster.password,
                                        "port": cluster.port,
                                        "hostname": cluster.hostname,
                                        "submit_commands": cluster.submit_commands,
                                        "workdir": cluster.workdir
                                    },
                                    "parameters": {
                                        "server_url": os.environ['DJANGO_API_URL'],
                                        "job_pk": job.pk,
                                        "token": job.token,
                                        "parameters": job.get_params(),
                                        "app_url_pattern": f"workflows:{workflow}:analyze",
                                        "icon_url": f"/assets/workflow_icons/{workflow}.png"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        response = client.execute(query, params)
        run_id = response['data']['startPipelineExecution']['run']['runId']
        job.status_set.create(state=Status.OK, description=f"Submitted pipeline with run_id '{run_id}'")
    except Exception as error:
        job.status_set.create(state=Status.FAILED, description=str(error))
        raise error

    return job.pk
