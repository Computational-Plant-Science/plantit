import paramiko


class SSHClient:
    def __init__(self, host: str, port: int, username: str, password: str = None):
        self.client = None
        self.port = port
        self.host = host
        self.username = username
        self.password = password

    def __enter__(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if self.password:
            client.connect(self.host, self.port, self.username, self.password)
        else:
            client.connect(self.host, self.port, self.username)

        self.client = client

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()