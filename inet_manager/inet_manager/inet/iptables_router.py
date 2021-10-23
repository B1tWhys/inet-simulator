from dataclasses import dataclass
from .container import BaseContainer
from ..util import docker_utils


@dataclass()
class ManuallyConfiguredRouter(BaseContainer):
    def __init__(self, name, as_):
        self.name = name
        self.as_list = [as_]
        self.container_id = self._init_container()

    def _init_container(self):
        return docker_utils.create_container('sleep infinity',
                                             name=self.name,
                                             network_id=self.as_list[0].docker_network_id,
                                             ipv4_forwarding=True)
