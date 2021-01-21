class RunOptions(object):
    def __init__(self,
                 identifier: str,
                 workdir: str,
                 image: str,
                 command: str,
                 mount: list = None,
                 api_url: str = None,
                 clone: str = None,
                 branch: str = None,
                 plantit_token: str = None,
                 cyverse_token: str = None,
                 docker_username: str = None,
                 docker_password: str = None,
                 params: list = None,
                 input: dict = None,
                 output: dict = None,
                 logging: dict = None,
                 checksums: list = None,
                 slurm: dict = None):
        self.identifier = identifier
        self.workdir = workdir
        self.image = image
        self.mount = mount
        self.api_url = api_url
        self.command = command
        self.clone = clone
        self.branch = branch
        self.plantit_token = plantit_token
        self.cyverse_token = cyverse_token
        self.docker_username = docker_username
        self.docker_password = docker_password
        self.params = params
        self.input = input
        self.output = output
        self.logging = logging
        self.checksums = checksums
        self.slurm = slurm