from plantit.notifications.models import DirectoryPolicyNotification, TargetPolicyNotification, Notification
from plantit.collections.utils import map_collection_policy


def map_directory_policy_notification(notification: DirectoryPolicyNotification):
    return {
        'id': notification.guid,
        'username': notification.user.username,
        'created': notification.created.isoformat(),
        'message': notification.message,
        'read': notification.read,
        'policy': map_collection_policy(notification.policy)
    }


def map_target_policy_notification(notification: TargetPolicyNotification):
    return {
        'id': notification.guid,
        'username': notification.user.username,
        'created': notification.created.isoformat(),
        'message': notification.message,
        'read': notification.read,
        'policy': {
            'user': notification.policy.user.username,
            'role': str(notification.policy.role.value)
        }
    }


def map_notification(notification: Notification):
    if isinstance(notification, DirectoryPolicyNotification):
        return map_directory_policy_notification(notification)
    elif isinstance(notification, TargetPolicyNotification):
        return map_target_policy_notification(notification)
    else:
        raise ValueError(f"Unrecognized notification type: {type(notification)}")