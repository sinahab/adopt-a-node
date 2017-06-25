
import os
from flask import current_app
from contextlib import contextmanager
import paramiko
import keyring

@contextmanager
def ssh_scope(ip_address, username):
    """Provide a transactional scope around a series of commands executed over ssh."""
    client = paramiko.SSHClient()

    keyfile = os.path.expanduser(current_app.config['SSH_PRIVATE_KEY_FILE'])
    password = keyring.get_password('SSH', keyfile)
    key = paramiko.RSAKey.from_private_key_file(keyfile, password=current_app.config['SSH_PRIVATE_KEY_PASSWORD'])

    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(ip_address, username=username, pkey=key)

    yield client

    client.close()
