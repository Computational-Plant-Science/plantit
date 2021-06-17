from plantit.notifications.models import Notification
from plantit.datasets.utils import map_dataset_policy


# def map_directory_policy_notification(notification: DirectoryPolicyNotification):
#     return {
#         'id': notification.guid,
#         'username': notification.user.username,
#         'created': notification.created.isoformat(),
#         'message': notification.message,
#         'read': notification.read,
#         'policy': map_dataset_policy(notification.policy)
#     }


def map_notification(notification: Notification):
    # if isinstance(notification, DirectoryPolicyNotification):
    #     return map_directory_policy_notification(notification)
    # else:
    return {
        'id': notification.guid,
        'username': notification.user.username,
        'created': notification.created.isoformat(),
        'message': notification.message,
        'read': notification.read,
    }
