from random import choice


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
