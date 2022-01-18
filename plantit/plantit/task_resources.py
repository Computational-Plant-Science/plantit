from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer

from plantit.keypairs import get_user_private_key_path
from plantit.queries import get_task_user, task_to_dict
from plantit.ssh import SSH
from plantit.tasks.models import Task


def get_task_ssh_client(task: Task) -> SSH:
    return SSH(
        host=task.agent.hostname,
        port=task.agent.port,
        username=task.agent.username,
        pkey=str(get_user_private_key_path(task.agent.user.username)))


async def push_task_channel_event(task: Task):
    user = await get_task_user(task)
    await get_channel_layer().group_send(f"{user.username}", {
        'type': 'task_event',
        'task': await sync_to_async(task_to_dict)(task),
    })
