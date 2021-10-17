from dataclasses import dataclass, field
from datetime import datetime
import autonomous_system


@dataclass
class Internet:
    name: str
    autonomous_systems: list[autonomous_system.AS] = field(default_factory=list)
    created_ts: datetime = datetime.now()
    last_modified_ts: datetime = datetime.now()
