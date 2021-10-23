from dataclasses import dataclass
import docker_utils


@dataclass
class BaseContainer:
    container_id: str
    name: str

    def cleanup_container(self):
        docker_utils.remove_container(self.container_id)
