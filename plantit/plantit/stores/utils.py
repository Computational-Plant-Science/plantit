from plantit.stores.models import DirectoryPolicy


def map_directory_policy(policy: DirectoryPolicy):
    return {
        'owner': policy.owner.username,
        'guest': policy.guest.username,
        'path': policy.path,
        'role': policy.role.value
    }