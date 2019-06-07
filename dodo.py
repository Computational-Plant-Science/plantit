'''
    A set of convenience commands for working with a production server.

    Used with the python package doit. Install doit with: pip install doit
'''
DOIT_CONFIG = {
                'default_tasks': [],
                'reporter': 'console'
              }

COMPOSE_CONFIG = '-f docker-compose.yml -f compose-prod.yml'

def task_rebuildContainers():
    '''
        Rebuild containers that have changed.
    '''
    return {
            'actions':  ['docker-compose %s up -d --build' % COMPOSE_CONFIG]
            }

def task_buildFrontEnd():
    '''
        Build the frontend code
    '''
    return {
        'actions': ['cd django/front_end; npm install; npm run build']
    }

def task_collectstatic():
    '''
        Collect the static (front end) files
    '''
    return {
            'actions': ['docker-compose %s exec djangoapp ./manage.py collectstatic --no-input' % COMPOSE_CONFIG],
        }

def task_makemigrations():
    '''
        Run django's 'manage.py makemigrations" command
    '''
    return {
        'actions': ['docker-compose %s exec djangoapp ./manage.py makemigrations' % COMPOSE_CONFIG],
    }

def task_migrate():
    '''
        Run django's 'manage.py migrate" command
    '''
    return {
        'actions': ['docker-compose %s exec djangoapp ./manage.py migrate' % COMPOSE_CONFIG],
    }

def task_restart():
    '''
        Restart the containers.
    '''
    return {
        'actions': ['docker-compose %s restart' % COMPOSE_CONFIG]
    }
