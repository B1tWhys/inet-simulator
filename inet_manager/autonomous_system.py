from dataclasses import dataclass
from ipaddress import IPv4Network
import docker_utils
import traceback


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
        try:
            docker_utils.remove_network(self.docker_network_id)
        except docker_utils.DockerException:
            traceback.print_exc()
