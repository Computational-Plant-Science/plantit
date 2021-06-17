import logging
from os import environ
from os.path import join
from pathlib import Path
from typing import List

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from plantit.datasets.models import DatasetAccessPolicy, DatasetSession

logger = logging.getLogger(__name__)


def map_dataset_policy(policy: DatasetAccessPolicy):
    return {
        'owner': policy.owner.username,
        'guest': policy.guest.username,
        'path': policy.path,
        'role': policy.role.value
    }


def map_dataset_session(session: DatasetSession):
    log_path = join(environ.get('SESSIONS_LOGS'), f"{session.guid}.session.log")
    if Path(log_path).exists():
        with open(log_path, 'r') as file:
            lines = file.readlines()
    else:
        lines = []

    return {
        'guid': session.guid,
        'path': session.path,
        'workdir': session.workdir,
        'agent': session.agent.name,
        'modified': session.modified if session.modified is not None else [],
        'output': lines,
        'opening': session.opening
    }


def update_dataset_session(session: DatasetSession, output: List[str]):
    log_path = join(environ.get('SESSIONS_LOGS'), f"{session.guid}.session.log")
    with open(log_path, 'a') as log:
        for line in output:
            log.write(f"{line}\n")

    if session.channel_name is not None:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(session.channel_name, {
            'type': 'update.session',
            'session': map_dataset_session(session),
        })