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


def get_container_ip(container_id, as_name) -> str:
    container = client.containers.get(container_id)
    container.reload()
    return container.attrs['NetworkSettings']['Networks'][as_name]['IPAddress']


def create_container(command, network_id, name=None, privileged=False, caps=None, environment=None):
    environment = environment if environment else {}
    caps = caps if caps else []
    container = client.containers.run(image='bgp-sandbox',
                                      name=name,
                                      cap_add=caps,
                                      command=command,
                                      detach=True,
                                      environment=environment,
                                      network=network_id,
                                      privileged=privileged,
                                      remove=True)
    return container.short_id


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


def remove_container(container_id):
    try:
        client.containers.get(container_id).remove(force=True)
    except docker.errors.DockerException as e:
        raise DockerException(e)
