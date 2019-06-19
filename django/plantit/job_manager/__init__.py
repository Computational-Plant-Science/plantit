'''
    The job manager provides a system for running ordered tasks asynchronously
    on the server side. Tasks are run on a `celery task queue <http://www.celeryproject.org>`_.
    This queue is run inside the celery docker container.

    The job manager's main purpose it to submit workflow runs to a cluster.
    However, can be used for any collection of ordered task that need run
    asynchronously with respect to the web server.

    Note:
        The celery container must be restarted to load any code changes.

    The major unit of the job manager is a :class:`job.Job`. A job contains a
    collection of ordered :class:`job.Task` that are run when the job is
    started. A job can be started by calling the static method
    :meth:`job.Job.run_next` passing the pk of the job to start.
    :meth:`~job.Job.run_next` will run the job's tasks sequentially starting with
    the task with the lowest :attr:`job.Job.Task.order_pos`.
    :meth:`~job.Job.run_next` will not run the next task in a job if
    the job's :meth:`~job.Job.current_status` is :attr:`job.Status.FAILED`.

    See the code for :class:`workflows.classes.Workflow` for an example of
    how to add tasks to a job and start the job.

    Workflow jobs are started by :class:`workflows.classes.Workflow`
'''
