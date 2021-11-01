from dataclasses import dataclass, field
from .autonomous_system import AS
from ipaddress import IPv4Network
from .containers import Container, Server, Client, ManualRouter, Router
from typing import Type, Union


class NamingConflictException(Exception):
    pass


@dataclass
class Internet:
    name: str
    _autonomous_systems: dict[int, AS] = field(default_factory=dict)
    subnet: IPv4Network = field(default_factory=lambda: IPv4Network('172.0.0.0/8'))
    containers: dict[str, Container] = field(default_factory=dict)

    def create_as(self, name: str):
        as_ = AS(name, self.next_asn(), self._next_as_subnet())
        self._autonomous_systems[as_.asn] = as_
        return as_

    def remove_as(self, as_: AS):
        as_.cleanup_docker_network()
        del self._autonomous_systems[as_.asn]

    def remove_asn(self, asn: int):
        self.remove_as(self.get_as(asn))

    def get_as(self, asn):
        return self._autonomous_systems[asn]

    def list_containers(self, container_type: Type[Container] = Container):
        return [c for c in self.containers.values() if isinstance(c, container_type)]

    def find_container(self, container_name) -> Union[Container, None]:
        return self.containers.get(container_name, None)

    def remove_container(self, container: Container):
        container.cleanup_container()
        del self.containers[container.name]

    def create_server(self, srv_name: str, as_: AS):
        if srv_name in self.containers:
            raise NamingConflictException(f"Server name: {srv_name} is already taken by another container")
        server = Server(srv_name, as_.name)
        self.containers[srv_name] = server

    def find_server(self, srv_name) -> Union[Server, None]:
        container = self.find_container(srv_name)
        return container if isinstance(container, Server) else None

    def create_client(self, client_name: str, as_: AS, server: Server):
        if client_name in self.containers:
            raise NamingConflictException(f"Client name: {client_name} is already taken by another container")
        client = Client(client_name, as_.name, server)
        self.containers[client_name] = client
        return client

    def find_client(self, client_name):
        container = self.find_container(client_name)
        return container if isinstance(container, Client) else None

    def create_manual_router(self, name, as_names):
        if name in self.containers:
            raise NamingConflictException(f"Router name: {name} is already taken by another container")
        router = ManualRouter(name, as_names)
        self.containers[name] = router

    def find_router(self, router_name):
        router = self.find_container(router_name)
        return router if isinstance(router, Router) else None

    def _next_as_subnet(self):
        current_subnets = [a.subnet for a in self._autonomous_systems.values()]
        for new in self.subnet.subnets(prefixlen_diff=8):
            overlaps = (new.overlaps(existing) for existing in current_subnets)
            if not any(overlaps):
                return new

    def list_autonomous_systems(self):
        return list(self._autonomous_systems.values())

    def get_autonomous_system_names(self):
        return list(self._autonomous_systems.keys())

    def get_all_servers(self):
        return [s for a in self.list_autonomous_systems() for s in a.list_servers()]

    def get_all_clients(self):
        return [c for a in self.list_autonomous_systems() for c in a.list_clients()]

    def get_all_routers(self):
        return [r for a in self.list_autonomous_systems() for r in a.list_routers()]

    def next_asn(self):
        current_asns = self._autonomous_systems.keys()
        if len(current_asns) == 0:
            return 1
        else:
            return max(current_asns) + 1

