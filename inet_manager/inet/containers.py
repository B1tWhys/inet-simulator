from dataclasses import dataclass

from ..util import docker_utils
from .interface import Interface


class InvalidContainerConfigurationException(Exception):
    pass


@dataclass
class Container:
    container_id: str
    name: str
    interfaces: list[Interface]

    def cleanup_container(self):
        docker_utils.remove_container(self.container_id)

    def run(self, command):
        docker_utils.run_command(self.container_id, command)

    def __repr__(self):
        return self.name


@dataclass
class Router(Container):
    pass


@dataclass
class ManualRouter(Router):
    def __init__(self, name, as_names: list[str]):
        self.name = name
        if len(as_names) == 0:
            raise InvalidContainerConfigurationException("Must specify at least 1 AS for a router to get created in")
        self.container_id = self._init_container(as_names[0])
        for as_name in as_names[1:]:
            docker_utils.connect_container_to_network(self.container_id, as_name)
        self.interfaces = docker_utils.get_container_interfaces(self.container_id)

    def _init_container(self, initial_net_name):
        return docker_utils.create_container('sleep infinity',
                                             name=self.name,
                                             network_name=initial_net_name,
                                             ipv4_forwarding=True)


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

    def configure_default_gateway(self, gateway_router: Router):
        for interface in gateway_router.interfaces:
            if self.interface.ip_interface.ip in interface.network:
                gateway_ip = interface.ip
                break
        else:
            err = f"Router {gateway_router.name} does not have an interface containing this container's IP address, " \
                  f"so it cannot be used as the default gateway"
            raise InvalidContainerConfigurationException(err)
        print(f"setting default gateway to: {gateway_ip}")
        self.run(f"set_gateway {gateway_ip}")



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
              f'--host "{self.target_server.ip}" ' \
              f'--port "{self.target_server.port}"'
        container = docker_utils.create_container(cmd,
                                                  name=self.name,
                                                  network_name=network_name)
        return container
