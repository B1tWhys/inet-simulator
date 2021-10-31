from dataclasses import dataclass
from ipaddress import IPv4Address

from .container import BaseContainer
from .server import Server
from ..util import docker_utils


@dataclass
class Client(BaseContainer):
    target_server: Server
    as_: object
    ip: IPv4Address

    def __init__(self, name, as_, target_server):
        self.name = name
        self.as_ = as_
        self.target_server = target_server
        self.container_id = self._init_container()
        self.ip = IPv4Address(docker_utils.get_container_ip(self.container_id, self.as_.name))

    def _init_container(self):
        cmd = f'python3 ./client/client.py ' \
              f'--host "{self.target_server.ip.compressed}" ' \
              f'--port "{self.target_server.port}"'
        container = docker_utils.create_container(cmd,
                                                  name=self.name,
                                                  network_id=self.as_.docker_network_id)
        return container
