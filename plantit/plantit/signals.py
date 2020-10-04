import json

from django.contrib.auth.models import User
from plantit.users.models import Profile


def cas_user_authenticated_callback(sender, **kwargs):
    args = {}
    args.update(kwargs)
    user = User.objects.get(username=args['username'])
    user.first_name = args['attributes']['firstName']
    user.last_name = args['attributes']['lastName']
    user.email = args['attributes']['email']
    user.save()
    print('''cas_user_authenticated_callback:
    user: %s
    created: %s
    attributes: %s
    ''' % (
        args.get('user'),
        args.get('created'),
        json.dumps(args.get('attributes'), sort_keys=True, indent=2)))


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
