from dataclasses import dataclass
from ipaddress import IPv4Network
import docker_utils


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
        self.docker_network_id = 'fixme'
