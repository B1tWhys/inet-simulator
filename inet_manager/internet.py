from dataclasses import dataclass, field
from datetime import datetime
import autonomous_system
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
        self.remove_asn(as_.asn)

    def remove_asn(self, asn: int):
        del self._autonomous_systems[asn]

    def _next_as_subnet(self):
        current_subnets = [a.subnet for a in self._autonomous_systems.values()]
        for new in self.subnet.subnets(prefixlen_diff=8):
            overlaps = (new.overlaps(existing) for existing in current_subnets)
            if not any(overlaps):
                return new

    def get_autonomous_systems(self):
        return list(self._autonomous_systems.values())

    def next_asn(self):
        current_asns = self._autonomous_systems.keys()
        if len(current_asns) == 0:
            return 1
        else:
            return max(current_asns) + 1
