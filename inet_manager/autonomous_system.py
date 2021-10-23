from dataclasses import dataclass
from ipaddress import IPv4Network
import docker_utils
import traceback
from server import Server
from iptables_router import ManuallyConfiguredRouter


@dataclass
class AS:
    name: str
    asn: int
    subnet: IPv4Network
    docker_network_id: str
    servers: dict[str, Server]

    def __init__(self, name, asn, subnet):
        self.name = name
        self.subnet = subnet
        self.asn = asn
        self.docker_network_id = self._create_docker_network()
        self.servers = {}
        self.routers = {}

    def _create_docker_network(self):
        return docker_utils.create_network(self.name, self.subnet)

    def cleanup_docker_network(self):
        docker_utils.remove_network(self.docker_network_id)

    def list_servers(self):
        return list(self.servers.values())

    def create_server(self, name):
        server = Server(name, self)
        self.servers[server.name] = server
        return server

    def remove_server(self, server):
        server.cleanup_container()
        del self.servers[server.name]

    def get_server(self, srv_name):
        return self.servers[srv_name]

    def create_manual_router(self, router_name):
        router = ManuallyConfiguredRouter(router_name, self)
        self.routers[router.name] = router
        return router

    def list_routers(self):
        return list(self.routers.values())

    def remove_router(self, router):
        router.cleanup_container()
        del self.routers[router.name]
