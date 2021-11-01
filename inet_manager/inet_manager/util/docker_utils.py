import docker
import docker.types
import docker.errors
from docker.models.networks import Network
from docker.models.containers import Container
from ipaddress import IPv4Network
from ..inet.interface import Interface

client = docker.from_env()


class DockerException(Exception):
    pass


def _safe_get_container(container_id) -> Container:
    return client.containers.get(container_id)


def get_containers() -> list[Container]:
    containers = client.containers.list()
    return containers


def get_container_interfaces(container_id) -> list[Interface]:
    container = _safe_get_container(container_id)
    container.reload()
    interfaces = []
    for name, net_info in container.attrs['NetworkSettings']['Networks'].items():
        interface = Interface(name, net_info['IPAddress'], net_info['IPPrefixLen'])
        interfaces.append(interface)
    return interfaces


def create_container(command, network_name,
                     name=None,
                     privileged=False,
                     caps=None,
                     environment=None,
                     ipv4_forwarding=False):
    sysctls = {'net.ipv4.ip_forward': 1} if ipv4_forwarding else {}
    environment = environment if environment else {}
    caps = caps if caps else ['CAP_NET_ADMIN']
    network_id = _find_network(network_name).id
    container = client.containers.run(image='bgp-sandbox',
                                      name=name,
                                      hostname=name,
                                      cap_add=caps,
                                      command=command,
                                      detach=True,
                                      environment=environment,
                                      network=network_id,
                                      privileged=privileged,
                                      sysctls=sysctls,
                                      remove=True)
    return container.short_id


def _find_network(network_name) -> Network:
    try:
        network = client.networks.list(network_name)[0]
    except IndexError:
        raise DockerException(f"Network {network_name} not found")
    return network


def rebuild_imgs():
    built_img = client.images.build(path='../../../docker', tag='bgp-sandbox')
    print(f"rebuilt {built_img}")


def create_network(name, subnet: IPv4Network):
    ipam_pool = docker.types.IPAMPool(subnet=str(subnet))
    ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
    network = client.networks.create(name, ipam=ipam_config)
    return network.id


def remove_network(id):
    try:
        client.networks.get(id).remove()
    except docker.errors.NotFound:
        pass
    except docker.errors.DockerException as e:
        raise DockerException(e)


def remove_container(container_id):
    try:
        _safe_get_container(container_id).remove(force=True)
    except docker.errors.DockerException as e:
        raise DockerException(e)


def connect_container_to_network(container_id, network_name):
    try:
        net = _find_network(network_name)
        net.connect(container_id)
    except docker.errors.DockerException as e:
        raise DockerException(e)


def run_command(container_id, command):
    container = _safe_get_container(container_id)
    _, resp_stream = container.exec_run(command, stream=True)
    for output in resp_stream:
        print(output.decode('ascii'), end='')
    print()
