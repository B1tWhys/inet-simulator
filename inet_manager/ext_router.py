from dataclasses import dataclass
from inet_manager.autonomous_system import AS
from inet_manager.container import BaseContainer

@dataclass
class ExtRouter(BaseContainer):
    as_: AS
    ixp: AS