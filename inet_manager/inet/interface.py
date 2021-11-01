import ipaddress


class Interface:
    as_name: str
    ip_interface: ipaddress.IPv4Interface

    def __init__(self, as_name, ip, prefix_len):
        self.as_name = as_name
        self.ip_interface = ipaddress.IPv4Interface((ip, prefix_len))

    @property
    def ip(self):
        return self.ip_interface.ip.compressed

    @property
    def network(self):
        return self.ip_interface.network
