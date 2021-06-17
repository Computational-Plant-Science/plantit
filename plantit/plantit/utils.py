import re
from random import choice

from plantit.tasks.options import BindMount


def parse_bind_mount(workdir: str, bind_mount: str) -> BindMount:
    split = bind_mount.rpartition(':')
    return BindMount(host_path=split[0], container_path=split[2]) if len(split) > 0 else BindMount(host_path=workdir, container_path=bind_mount)


def format_bind_mount(workdir: str, bind_mount: BindMount) -> str:
    return bind_mount['host_path'] + ':' + bind_mount['container_path'] if bind_mount['host_path'] != '' else workdir + ':' + bind_mount['container_path']


def get_csrf_token(request) -> str:
    token = request.session.get('csrfToken', None)
    if token is None:
        token = generate_secret_key()
        request.session['csrfToken'] = token
    return token


def generate_random_string(length: int, allowed_chars='abcdefghijklmnopqrstuvwxyz' 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') -> str:
    return ''.join(choice(allowed_chars) for i in range(length))


def generate_secret_key() -> str:
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return generate_random_string(40, chars)


def clean_html(raw_html: str) -> str:
    expr = re.compile('<.*?>')
    text = re.sub(expr, '', raw_html)
    return text