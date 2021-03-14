from plantit.collections.models import CollectionAccessPolicy


def map_collection_policy(policy: CollectionAccessPolicy):
    return {
        'owner': policy.owner.username,
        'guest': policy.guest.username,
        'path': policy.path,
        'role': policy.role.value
    }