from os import listdir
from os.path import join, isfile
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


def list_local_files(path,
                     include_patterns=None,
                     include_names=None,
                     exclude_patterns=None,
                     exclude_names=None):
    """
    Lists local files under the given path (matching optional filtering parameters, if provided).

    Args:
        path: The directory path
        include_patterns: Filename patterns to include
        include_names: Filenames to include
        exclude_patterns: Filename patterns to exclude
        exclude_names: Filenames to exclude

    Returns: A list of filenames matching the given criteria
    """

    # gather all files
    all_paths = [join(path, file) for file in listdir(path) if isfile(join(path, file))]

    # add files matching included patterns
    included_by_pattern = [pth for pth in all_paths if any(
        pattern.lower() in pth.lower() for pattern in include_patterns)] if include_patterns is not None else all_paths

    # add files included by name
    included_by_name = ([pth for pth in all_paths if pth.rpartition('/')[2] in [name for name in include_names]] \
                            if include_names is not None else included_by_pattern) + \
                       [pth for pth in all_paths if pth in [name for name in include_names]] \
        if include_names is not None else included_by_pattern

    # gather only included files
    included = list(set(included_by_pattern + included_by_name))

    # remove files matched excluded patterns
    excluded_by_pattern = [name for name in included if all(pattern.lower() not in name.lower() for pattern in
                                                            exclude_patterns)] if exclude_patterns is not None else included

    # remove files excluded by name
    excluded_by_name = [pattern for pattern in excluded_by_pattern if pattern.split('/')[
        -1] not in exclude_names] if exclude_names is not None else excluded_by_pattern

    return excluded_by_name
