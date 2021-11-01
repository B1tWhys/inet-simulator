from dataclasses import dataclass
import ipaddress


class Interface:
    as_name: str
    _interface: ipaddress.IPv4Interface

    def __init__(self, as_name, ip, prefix_len):
        self.as_name = as_name
        self._interface = ipaddress.IPv4Interface((ip, prefix_len))

    @property
    def ip(self):
        return self._interface.ip.compressed

    @property
    def network(self):
        return self._interface.network.compressed
