import re
from random import choice

from plantit.tasks.options import BindMount


def clean_html(raw_html: str) -> str:
    expr = re.compile('<.*?>')
    text = re.sub(expr, '', raw_html)
    return text


def del_none(d) -> dict:
    """
    Delete keys with the value ``None`` in a dictionary, recursively.

    This alters the input so you may wish to ``copy`` the dict first.

    Referenced from https://stackoverflow.com/a/4256027.
    """
    # For Python 3, write `list(d.items())`; `d.items()` won’t work
    # For Python 2, write `d.items()`; `d.iteritems()` won’t work
    for key, value in list(d.items()):
        if value is None:
            del d[key]
        elif isinstance(value, dict):
            del_none(value)
    return d  # For convenience


def generate_secret_key() -> str:
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return generate_random_string(40, chars)


def generate_random_string(length: int, allowed_chars='abcdefghijklmnopqrstuvwxyz' 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') -> str:
    return ''.join(choice(allowed_chars) for i in range(length))


def get_csrf_token(request) -> str:
    token = request.session.get('csrfToken', None)
    if token is None:
        token = generate_secret_key()
        request.session['csrfToken'] = token
    return token


def format_bind_mount(workdir: str, bind_mount: BindMount) -> str:
    return bind_mount['host_path'] + ':' + bind_mount['container_path'] if bind_mount['host_path'] != '' else workdir + ':' + bind_mount[
        'container_path']


def parse_bind_mount(workdir: str, bind_mount: str) -> BindMount:
    split = bind_mount.rpartition(':')
    return BindMount(host_path=split[0], container_path=split[2]) if len(split) > 0 else BindMount(host_path=workdir, container_path=bind_mount)