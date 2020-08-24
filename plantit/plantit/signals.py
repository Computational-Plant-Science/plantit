import json


def cas_user_authenticated_callback(sender, **kwargs):
    args = {}
    args.update(kwargs)
    print('''cas_user_authenticated_callback:
    user: %s
    created: %s
    attributes: %s
    request: %s
    ''' % (
        args.get('user'),
        args.get('created'),
        json.dumps(args.get('attributes'), sort_keys=True, indent=2),
        json.dumps(args.get('request'))))


def cas_user_logout_callback(sender, **kwargs):
    args = {}
    args.update(kwargs)
    print('''cas_user_logout_callback:
    user: %s
    session: %s
    ticket: %s
    ''' % (
        args.get('user'),
        args.get('session'),
        args.get('ticket')))
