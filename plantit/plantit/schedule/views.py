import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, JsonResponse, HttpResponseNotAllowed
from django_celery_beat.models import CrontabSchedule

from plantit.agents.models import Agent, AgentTask
from plantit.tasks.models import DelayedTask
from plantit.utils import agent_task_to_dict, delayed_task_to_dict


@login_required
def search_or_add_agent_task(request):
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        task_name = body['name']
        task_description = body['description']
        task_command = body['command']
        task_delay = body['delay'].split()
        agent_name = body['agent_name']

        try:
            agent = Agent.objects.get(name=agent_name)
        except:
            return HttpResponseNotFound()

        if agent.user.username != request.username:
            return HttpResponseNotAllowed()

        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=task_delay[0],
            hour=task_delay[1],
            day_of_week=task_delay[2],
            day_of_month=task_delay[3],
            month_of_year=task_delay[4])
        task, created = AgentTask.objects.get_or_create(
            crontab=schedule,
            agent=agent,
            name=task_name,
            command=task_command,
            description=task_description,
            task='plantit.celery_tasks.execute_agent_command',
            args=json.dumps([agent.name, task_command]))

        return JsonResponse({
            'task': agent_task_to_dict(task),
            'created': created
        })


@login_required
def get_or_delete_agent_task(request, name):
    try:
        task = AgentTask.objects.get(name=name)
    except:
        return HttpResponseNotFound()

    if request.method == 'GET':
        return JsonResponse(agent_task_to_dict(task))
    elif request.method == 'DELETE':
        task.delete()
        return JsonResponse({'deleted': True})
    else:
        return HttpResponseNotAllowed(['GET', 'DELETE'])


@login_required
def toggle_agent_task(request, name):
    try:
        task = AgentTask.objects.get(name=name)
    except:
        return HttpResponseNotFound()

    task.enabled = not task.enabled
    task.save()
    return JsonResponse({'enabled': task.enabled})


@login_required
def search_or_add_delayed_task(request):
    body = json.loads(request.body.decode('utf-8'))
    task_name = body['name']
    task_description = body['description']
    task_command = body['command']
    task_delay = body['delay'].split()

    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=task_delay[0],
        hour=task_delay[1],
        day_of_week=task_delay[2],
        day_of_month=task_delay[3],
        month_of_year=task_delay[4])
    task, created = DelayedTask.objects.get_or_create(
        crontab=schedule,
        name=task_name,
        command=task_command,
        description=task_description,
        task='plantit.celery_tasks.execute_agent_command',
        args=json.dumps([task_command]))

    return JsonResponse({
        'task': agent_task_to_dict(task),
        'created': created
    })


@login_required
def get_or_delete_delayed_task(request, name):
    try:
        task = DelayedTask.objects.get(name=name)
    except:
        return HttpResponseNotFound()

    if request.method == 'GET':
        return JsonResponse(delayed_task_to_dict(task))
    elif request.method == 'DELETE':
        task.delete()
        return JsonResponse({'deleted': True})
    else:
        return HttpResponseNotAllowed(['GET', 'DELETE'])


@login_required
def toggle_delayed_task(request, name):
    try:
        task = DelayedTask.objects.get(name=name)
    except:
        return HttpResponseNotFound()

    task.enabled = not task.enabled
    task.save()
    return JsonResponse({'enabled': task.enabled})
