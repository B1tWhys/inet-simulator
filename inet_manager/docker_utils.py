import docker

client = docker.from_env()


def get_containers():
    containers = client.containers.list()
    return containers


def rebuild_imgs():
    built_img = client.images.build(path='../docker', tag='bgp-sandbox')
    print(f"rebuilt {built_img}")
