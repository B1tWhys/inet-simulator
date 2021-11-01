from dataclasses import dataclass

from ..util import docker_utils
from .interface import Interface


@dataclass
class Container:
    container_id: str
    name: str
    interfaces: list[Interface]

    def cleanup_container(self):
        docker_utils.remove_container(self.container_id)

    def __repr__(self):
        return self.name


@dataclass
class SingleInterfaceContainer(Container):
    @property
    def interface(self):
        return self.interfaces[0]

    @property
    def ip(self):
        return self.interface.ip

    @property
    def as_name(self):
        return self.interface.as_name


@dataclass
class Server(SingleInterfaceContainer):
    port: int

    def __init__(self, name, as_name, port=8000):
        self.name = name
        self.port = port
        self.container_id = self._create_container(as_name)
        self.interfaces = docker_utils.get_container_interfaces(self.container_id)

    def _create_container(self, network_name):
        env = {'PORT': self.port}
        container = docker_utils.create_container('python3 ./server/server.py',
                                                  name=self.name,
                                                  network_name=network_name,
                                                  environment=env)
        return container


@dataclass
class Client(SingleInterfaceContainer):
    target_server: Server

    def __init__(self, name, as_name, target_server: Server):
        self.name = name
        self.target_server = target_server
        self.container_id = self._init_container(as_name)
        self.interfaces = docker_utils.get_container_interfaces(self.container_id)

    def _init_container(self, network_name):
        cmd = f'python3 ./client/client.py ' \
              f'--host "{self.target_server.ip.compressed}" ' \
              f'--port "{self.target_server.port}"'
        container = docker_utils.create_container(cmd,
                                                  name=self.name,
                                                  network_name=network_name)
        return container


@dataclass
class ManuallyConfiguredRouter(Container):
    def __init__(self, name, as_):
        self.name = name
        self.as_list = [as_]
        self.container_id = self._init_container()

    def _init_container(self):
        return docker_utils.create_container('sleep infinity',
                                             name=self.name,
                                             network_id=self.as_list[0].docker_network_id,
                                             ipv4_forwarding=True)
