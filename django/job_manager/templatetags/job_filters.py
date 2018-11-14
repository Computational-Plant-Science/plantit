from django import template
register = template.Library()

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
