"""
    A set of convenience commands for working with a production server.

    Used with the python package doit. Install doit with: pip install doit
"""
DOIT_CONFIG = {
    'default_tasks': [],
    'reporter': 'console'
}

COMPOSE_CONFIG = '-f docker-compose.yml -f docker-compose.prod.yml'


def task_rebuildContainers():
    """
        Rebuild containers that have changed.
    """
    return {
        'actions': ['docker-compose %s up -d --build' % COMPOSE_CONFIG]
    }


def task_buildFrontEnd():
    '''
        Build the frontend code
    '''
    return {
        'actions': ['cd plantit/front_end; npm install; npm run build']
    }


def task_collectstatic():
    '''
        Collect the static (front end) files
    '''
    return {
        'actions': ['docker-compose %s exec plantit ./manage.py collectstatic --no-input' % COMPOSE_CONFIG],
    }


def task_makemigrations():
    '''
        Run django's 'manage.py makemigrations" command
    '''
    return {
        'actions': ['docker-compose %s exec plantit ./manage.py makemigrations' % COMPOSE_CONFIG],
    }


def task_migrate():
    '''
        Run django's 'manage.py migrate" command
    '''
    return {
        'actions': ['docker-compose %s exec plantit ./manage.py migrate' % COMPOSE_CONFIG],
    }


def task_restart():
    '''
        Restart the containers.
    '''
    return {
        'actions': ['docker-compose %s restart' % COMPOSE_CONFIG]
    }
