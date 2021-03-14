from os import environ
from os.path import join
from pathlib import Path
from typing import List

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from plantit.sessions.models import Session


def map_session(session: Session):
    workdir = join(session.cluster.workdir, session.workdir)
    log_path = join(environ.get('SESSIONS_LOGS'), f"{session.guid}.session.log")
    if Path(log_path).exists():
        with open(log_path, 'r') as file:
            lines = file.readlines()
    else:
        lines = []

    return {
        'guid': session.guid,
        'workdir': workdir,
        'cluster': session.cluster.name,
        'output': lines
    }


def update_session(session: Session, output: List[str]):
    log_path = join(environ.get('SESSIONS_LOGS'), f"{session.guid}.session.log")
    with open(log_path, 'a') as log:
        for line in output:
            log.write(f"{line}\n")

    async_to_sync(get_channel_layer().group_send)(f"sessions-{session.user.username}-{session.cluster.name}", {
        'type': 'session_update',
        'session': map_session(session)
    })
