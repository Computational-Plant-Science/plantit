from random import choice

import numpy as np


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


def rescale(value, r_min, r_max, t_min=0, t_max=1):
    """
    Scales the value (to the unit interval [0, 1] by default). Strategy from https://stats.stackexchange.com/a/281164/338214.

    :param value: The value to scale
    :param r_min: The minimum of the range the input value is scaled according to
    :param r_max: The maximum of the range the input value is scaled according to
    :param t_min: The minimum of the target range (defaults to 0)
    :param t_max: The maximum of the target range (defaults to 1)
    :return: The rescaled value
    """

    return (value - r_min) / (r_max - r_min) * (t_max - t_min) + t_min

def jitter(x, amount):
    """
    Adds a tunable amount of random noise to the input array. Adapted from https://stackoverflow.com/a/21276920/6514033.

    :param x: The input array
    :param amount: The noise multiplier
    :return:
    """

    sd = .01 * amount * (np.max(x) - np.min(x))
    return x + np.random.randn(len(x)) * sd
