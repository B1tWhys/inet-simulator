from ..util import docker_utils

from .container import BaseContainer
from dataclasses import dataclass
from ipaddress import IPv4Address


@dataclass
class Server(BaseContainer):
    port: int
    ip: IPv4Address

    def __init__(self, name, as_, port=8000):
        self.name = name
        self.as_ = as_
        self.port = port
        self.container_id = self._init_container()
        self.ip = IPv4Address(docker_utils.get_container_ip(self.container_id, self.as_.name))

    def _init_container(self):
        env = {'PORT': self.port}
        container = docker_utils.create_container('python3 ./server/server.py',
                                                  name=self.name,
                                                  network_id=self.as_.docker_network_id,
                                                  environment=env)
        return container
