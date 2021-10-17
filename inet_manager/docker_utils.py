import docker
import docker.types
import docker.errors
from ipaddress import IPv4Network

client = docker.from_env()


class DockerException(Exception):
    pass


def get_containers():
    containers = client.containers.list()
    return containers


def rebuild_imgs():
    built_img = client.images.build(path='../docker', tag='bgp-sandbox')
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
