from abc import ABCMeta, abstractmethod

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User

from plantit_web.cache import ModelViews
from plantit_web.notifications.models import Notification
from plantit_web.tasks.models import Task
from plantit_web.users.models import Migration, ManagedFile


class ChannelsBase(metaclass=ABCMeta):
    def __init__(self, views: ModelViews):
        self.__views = views

    @abstractmethod
    def push_task_event(self, task: Task):
        pass

    @abstractmethod
    def push_notification_event(self, notification: Notification):
        pass

    @abstractmethod
    def push_migration_event(self, user: User, migration: Migration, file: ManagedFile = None):
        pass


class Channels(ChannelsBase):
    def __init__(self, views: ModelViews):
        super(Channels, self).__init__(views)

    def push_task_event(self, task: Task):
        async_to_sync(get_channel_layer().group_send)(f"{task.user.username}", {
            'type': 'task_event',
            'task': self.__views.task_to_dict(task),
        })

    def push_notification_event(self, notification: Notification, recipient: User = None):
        recipient_username = recipient if recipient is not None else notification.user.username
        async_to_sync(get_channel_layer().group_send)(recipient_username, {
            'type': 'push_notification',
            'notification': {
                'id': notification.guid,
                'username': notification.user.username,
                'created': notification.created.isoformat(),
                'message': notification.message,
                'read': notification.read,
            }
        })

    def push_migration_event(self, user: User, migration: Migration, file: ManagedFile = None):
        data = {
            'type': 'migration_event',
            'migration': ModelViews.migration_to_dict(migration),
        }
        if file is not None: data['file'] = ModelViews.managed_file_to_dict(file)
        async_to_sync(get_channel_layer().group_send)(f"{user.username}", data)


class AsyncChannels(ChannelsBase):
    def __init__(self, views: ModelViews):
        super(AsyncChannels, self).__init__(views)

    async def push_task_event(self, task: Task):
        await get_channel_layer().group_send(f"{task.user.username}", {
            'type': 'task_event',
            'task': self.__views.task_to_dict(task),
        })

    async def push_notification_event(self, notification: Notification, recipient: User = None):
        recipient_username = recipient if recipient is not None else notification.user.username
        await get_channel_layer().group_send(recipient_username, {
            'type': 'push_notification',
            'notification': {
                'id': notification.guid,
                'username': notification.user.username,
                'created': notification.created.isoformat(),
                'message': notification.message,
                'read': notification.read,
            }
        })

    async def push_migration_event(self, user: User, migration: Migration, file: ManagedFile = None):
        data = {
            'type': 'migration_event',
            'migration': ModelViews.migration_to_dict(migration),
        }
        if file is not None: data['file'] = ModelViews.managed_file_to_dict(file)
        await get_channel_layer().group_send(f"{user.username}", data)
