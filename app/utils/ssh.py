
from contextlib import contextmanager
import paramiko

@contextmanager
def ssh_scope(ip_address, username):
    """Provide a transactional scope around a series of commands executed over ssh."""
    client = paramiko.SSHClient()

    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(ip_address, username=username)

    yield client

    client.close()
