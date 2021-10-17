import docker

client = docker.from_env()

def get_containers():
    containers = client.containers.list()
    return containers
