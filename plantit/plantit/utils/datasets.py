from plantit.datasets.models import DatasetAccessPolicy


def dataset_access_policy_to_dict(policy: DatasetAccessPolicy):
    return {
        'owner': policy.owner.username,
        'guest': policy.guest.username,
        'path': policy.path,
        'role': policy.role.value
    }