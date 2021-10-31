from dataclasses import dataclass
from ..util import docker_utils


@dataclass
class BaseContainer:
    container_id: str
    name: str

    def cleanup_container(self):
        docker_utils.remove_container(self.container_id)

    def __repr__(self):
        return self.name
