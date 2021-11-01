from dataclasses import dataclass
from ipaddress import IPv4Network
from ..util import docker_utils


@dataclass
class AS:
    name: str
    asn: int
    subnet: IPv4Network
    docker_network_id: str

    def __init__(self, name, asn, subnet):
        self.name = name
        self.subnet = subnet
        self.asn = asn
        self.docker_network_id = self._create_docker_network()

    def _create_docker_network(self):
        return docker_utils.create_network(self.name, self.subnet)

    def cleanup_docker_network(self):
        docker_utils.remove_network(self.docker_network_id)