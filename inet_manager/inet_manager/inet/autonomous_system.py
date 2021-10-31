from dataclasses import dataclass
from ipaddress import IPv4Network
from ..util import docker_utils
from .server import Server
from .client import Client
from .iptables_router import ManuallyConfiguredRouter


@dataclass
class AS:
    name: str
    asn: int
    subnet: IPv4Network
    docker_network_id: str
    servers: dict[str, Server]
    clients: dict[str, Client]

    def __init__(self, name, asn, subnet):
        self.name = name
        self.subnet = subnet
        self.asn = asn
        self.docker_network_id = self._create_docker_network()
        self.servers = {}
        self.routers = {}
        self.clients = {}

    def _create_docker_network(self):
        return docker_utils.create_network(self.name, self.subnet)

    def cleanup_docker_network(self):
        docker_utils.remove_network(self.docker_network_id)

    def list_servers(self):
        return list(self.servers.values())

    def list_clients(self):
        return list(self.clients.values())

    def create_server(self, name):
        server = Server(name, self)
        self.servers[name] = server
        return server

    def create_client(self, name, target_server):
        client = Client(name, self, target_server)
        self.clients[name] = client
        return client

    def remove_server(self, server):
        server.cleanup_container()
        del self.servers[server.name]

    def remove_client(self, client):
        client.cleanup_container()
        del self.clients[client.name]

    def get_server(self, srv_name):
        return self.servers[srv_name]

    def get_client(self, client_name):
        return self.clients[client_name]

    def create_manual_router(self, router_name):
        router = ManuallyConfiguredRouter(router_name, self)
        self.routers[router.name] = router
        return router

    def list_routers(self):
        return list(self.routers.values())

    def remove_router(self, router):
        router.cleanup_container()
        del self.routers[router.name]
