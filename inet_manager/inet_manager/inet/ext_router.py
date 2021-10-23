from dataclasses import dataclass
from .autonomous_system import AS
from .container import BaseContainer

@dataclass
class ExtRouter(BaseContainer):
    as_: AS
    ixp: AS