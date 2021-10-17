from ipaddress import IPv4Address
from dataclasses import dataclass
from .autonomous_system import AS

@dataclass
class BaseContainer:
    container_id: str
    image: str
    