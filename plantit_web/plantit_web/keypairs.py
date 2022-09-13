import subprocess
import logging
from os.path import join
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)


def get_or_create_user_keypair(username: str, overwrite: bool = False) -> str:
    """
    Creates an RSA-protected SSH keypair for the user and returns the public key (or gets the public key if a keypair already exists).
    To overwrite a pre-existing keypair, use the `invalidate` argument.

    Args:
        username: The user (CyVerse/Django username) to create a keypair for.
        overwrite: Whether to overwrite an existing keypair.

    Returns: The path to the newly created public key.
    """
    public_key_path = get_user_public_key_path(username)
    private_key_path = get_user_private_key_path(username)

    if public_key_path.is_file():
        if overwrite:
            logger.info(f"Keypair for {username} already exists, overwriting")
            public_key_path.unlink()
            private_key_path.unlink(missing_ok=True)
        else:
            logger.info(f"Keypair for {username} already exists")
    else:
        subprocess.run(f"ssh-keygen -b 2048 -t rsa -f {private_key_path} -N \"\"", shell=True)
        logger.info(f"Created keypair for {username}")

    with open(public_key_path, 'r') as key:
        return key.readlines()[0]


def get_user_private_key_path(username: str) -> Path:
    path = Path(f"{Path(settings.AGENT_KEYS).absolute()}/{username}")
    path.mkdir(exist_ok=True, parents=True)
    return Path(join(path, f"{username}_id_rsa"))


def get_user_public_key_path(username: str) -> Path:
    path = Path(f"{Path(settings.AGENT_KEYS).absolute()}/{username}")
    path.mkdir(exist_ok=True, parents=True)
    return Path(join(path, f"{username}_id_rsa.pub"))