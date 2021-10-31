from dataclasses import dataclass, field
from datetime import datetime
from . import autonomous_system
from ipaddress import IPv4Network


@dataclass
class Internet:
    name: str
    _autonomous_systems: dict[int, autonomous_system.AS] = field(default_factory=dict)
    created_ts: datetime = datetime.now()
    last_modified_ts: datetime = datetime.now()
    subnet: IPv4Network = field(default_factory=lambda: IPv4Network('172.0.0.0/8'))

    def create_as(self, name: str):
        as_ = autonomous_system.AS(name, self.next_asn(), self._next_as_subnet())
        self._autonomous_systems[as_.asn] = as_
        return as_

    def remove_as(self, as_: autonomous_system.AS):
        as_.cleanup_docker_network()
        del self._autonomous_systems[as_.asn]

    def remove_asn(self, asn: int):
        self.remove_as(self.get_as(asn))

    def get_as(self, asn):
        return self._autonomous_systems[asn]

    def find_servers(self, srv_name):
        ret = []
        for a in self.list_autonomous_systems():
            try:
                ret.append(a.get_server(srv_name))
            except KeyError:
                pass
        return ret

    def find_clients(self, client_name):
        ret = []
        for a in self.list_autonomous_systems():
            try:
                ret.append(a.get_client(client_name))
            except KeyError:
                pass
        return ret

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


