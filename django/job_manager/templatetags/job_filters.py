from django import template

from job_manager.job import Status

register = template.Library()

@register.filter()
def has_failed(job):
    """
        Returns
    """
    state = job.current_status()

    return state.state == Status.FAILED

@register.filter()
def current_status(job):
    """
        Get the human readable (i.e. as a string) latest status of the job.

        Args:
            job: the job to extract the state from
    """

    state = job.current_status()

    return str(state)

@register.filter()
def current_status_date(job):
    """
        Get the human readable (i.e. as a string) latest status of the job.

        Args:
            job: the job to extract the state from
    """

    state = job.current_status()

    return state.date

@register.filter()
def current_status_description(job):
    """
        Get the latest status description.

        Args:
            job: the job to extract the state from
    """

    state = job.current_status()
    return state.description


@register.filter()
def status_set(job):
    """
        Get a list of all status updates

        Adds "state_str" convience attribute to the status objects that
        provides a human readable (i.e. string) of the job status.

        Args:
            job: the job to extract the statuses from
    """
    states = job.status_set.all()

    for s in states:
        s.state_str = str(s)

    return states

@register.filter()
def tasks(job):
    """
        Get a list of the job tasks

        Args:
            job: the job to extract the statuses from
    """
    tasks = job.task_set.all().order_by('order_pos').select_subclasses()

    return tasks

@register.filter()
def results(job):
    query = job.result_set.select_subclasses()
    results = []
    for obj in query:
        results.append(obj.serialize())

    return results
