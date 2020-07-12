import paramiko


class SSH:
    def __init__(self, host: str, port: int, username: str, password: str = None):
        self.client = None
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def __enter__(self):
        client = paramiko.SSHClient()
        client.load_host_keys('../config/ssh/known_hosts')
        client.set_missing_host_key_policy(paramiko.RejectPolicy())

        if self.password:
            client.connect(self.host, self.port, self.username, self.password)
        else:
            key = paramiko.RSAKey.from_private_key_file('../config/ssh/id_rsa')
            client.connect(self.host, self.port, self.username, pkey=key)

        self.client = client

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()
