from ..util import docker_utils, storage
from ..inet.internet import Internet
from .printing import *
from ..inet.containers import *

from itertools import count
import click
import inquirer
from typing import *

pass_inet = click.make_pass_decorator(Internet, ensure=True)
inet: Internet


@click.group()
@click.pass_context
def root(ctx):
    def save():
        if inet is not None:
            storage.save_inet(inet)

    global inet
    inet = _select_internet()
    ctx.call_on_close(save)


@root.group("docker")
def docker():
    pass


@docker.command("rebuild")
def build():
    docker_utils.rebuild_imgs()


@root.group("new")
def new():
    pass


@new.command("as")
@click.argument("name", required=False)
def new_as(name: str):
    existing_names = {a.name for a in inet.list_autonomous_systems()}
    if not name:
        default_name = f"as-{inet.next_asn()}"
        name = _prompt_for_new_name("enter name for new AS: ", existing_names, default=default_name)
    if name in existing_names:
        print(f"{name} already exists. Chose another name")
        return
    inet.create_as(name)


@new.command("server")
def new_server():
    as_ = _select_as('select AS to create the server in:')
    if as_ is None:
        print("You need to create an AS first")
        return

    current_names = [s.name for s in inet.list_containers(Server)]
    default = _gen_default_name(f'server{as_.asn}-', current_names)
    name = _prompt_for_new_name("enter name for new server: ", existing_names=current_names, default=default)
    inet.create_server(name, as_)


@new.command("client")
def new_client():
    as_ = _select_as('select AS to create client in:')
    if as_ is None:
        print("You need to create an AS first")
        return
    current_names = [s.name for s in inet.list_containers(Client)]
    server = _select_server('select server for client to make requests to')
    if server is None:
        print("No servers exist for the client to make requests to. Create a server first!")
        exit(1)
    default = _gen_default_name(f'client{as_.asn}-', current_names)
    name = _prompt_for_new_name("enter name for new client: ", existing_names=current_names, default=default)
    inet.create_client(name, as_, server)


@new.command("router")
def new_router():
    # TODO: once multiple types of routers are supported, prompt the user for the router type
    _new_manual_router()


def _new_manual_router():
    all_as_names = [a.name for a in inet.list_autonomous_systems()]
    current_names = [c.name for c in inet.list_containers()]
    default_name = _gen_default_name(f'router-', current_names)
    as_names = inquirer.prompt([
        inquirer.Checkbox('as',
                          message="which as's should this router be attached to? "
                                  "(Select at least 1, you can attach more later)",
                          choices=all_as_names)])['as']
    name = _prompt_for_new_name("enter name for new router: ", existing_names=current_names, default=default_name)
    inet.create_manual_router(name, as_names)


@root.group("rm")
def rm():
    pass


@rm.command("as")
def rm_as():
    choices = [(a.name, a) for a in inet.list_autonomous_systems()]
    if len(choices) == 0:
        print("There arent any as's to remove")
        return
    answer = inquirer.prompt([inquirer.List('as', message='select as to remove', choices=choices)])
    as_ = answer['as']
    inet.remove_as(as_)


@rm.command("server")
@click.argument("srv_name", required=False)
def rm_container(srv_name):
    if srv_name is None:
        container = _select_server("select server to remove: ")
    else:
        container = inet.find_server(srv_name)
        if container is None:
            print(f"Server {srv_name} not found!")
            exit(1)
    inet.remove_container(container)


@rm.command("client")
@click.argument("client_name", required=False)
def rm_client(client_name):
    if client_name is None:
        client = _select_client("Select client to remove: ")
    else:
        client = inet.find_client(client_name)
        if client is None:
            print(f"Client {client} not found!")
            exit(1)
    inet.remove_container(client)


@rm.command("router")
@click.argument("router_name", required=False)
def rm_router(router_name):
    if router_name is None:
        router = _select_container("Select router to remove: ", Router)
    else:
        router = inet.find_router(router_name)
        if router is None:
            print(f"Router {router} not found!")
            exit(1)
    inet.remove_container(router)


@rm.command("state")
def rm_state():
    global inet
    storage.rm_state()
    inet = None


@root.group("ls")
def ls():
    pass


@ls.command("as")
def ls_as():
    print_as_table(inet.list_autonomous_systems())


@ls.command("servers")
def ls_servers():
    servers = inet.list_containers(Server)
    print_single_interface_container_table(servers)


@ls.command("clients")
def ls_clients():
    clients = inet.list_containers(Client)
    print_single_interface_container_table(clients)


@ls.command("routers")
def ls_routers():
    routers = inet.list_containers(Router)
    print(routers)


@root.group("configure")
def configure():
    pass


@configure.command("default-route")
@click.argument("container-name")
@click.argument("gateway-name")
def configure_default_route(container_name, gateway_name):
    container = inet.find_container(container_name)
    if container is None:
        print(f"Container {container_name} not found!")
        exit(1)
    elif not isinstance(container, SingleInterfaceContainer):
        print(f"Cannot configure default route on a router!")
        exit(1)
    gateway = inet.find_router(gateway_name)
    if gateway is None:
        print(f"Router {gateway_name} not found!")
        exit(1)

    container.configure_default_gateway(gateway)


def _prompt_for_new_name(message, existing_names, default=None):
    return inquirer.text(message=message, validate=lambda c, m: m not in existing_names, default=default)


def _gen_default_name(prefix, existing_names):
    for i in count(1):
        name = prefix + str(i)
        if name not in existing_names:
            return name


def _create_internet():
    existing_names = storage.get_saved_inet_names()
    default_name = _gen_default_name('inet-', existing_names)
    name = _prompt_for_new_name("enter name for new internet", existing_names, default=default_name)
    return Internet(name=name)


def _select_internet():
    inet_names = storage.get_saved_inet_names()
    if len(inet_names) == 0:
        return _create_internet()
    elif len(inet_names) == 1:
        return storage.load_inet(inet_names[0])
    else:
        answer = inquirer.prompt([inquirer.List('inet_name',
                                                message="select internet to operate on",
                                                choices=inet_names)])
        return storage.load_inet(answer['inet_name'])


def _select_as(message) -> Union[AS, None]:
    choices = [(a.name, a) for a in inet.list_autonomous_systems()]
    if len(choices) == 0:
        return None
    elif len(choices) == 1:
        print(f"only one AS exists so I assume the one you want is {choices[0][0]}")
        return choices[0][1]
    answer = inquirer.prompt([inquirer.List('as', message=message, choices=choices)])
    as_ = answer['as']
    return as_


def _select_container(message, container_type):
    choices = [(c.name, c) for c in inet.list_containers(container_type=container_type)]
    if len(choices) == 0:
        return None
    elif len(choices) == 1:
        print(f"Only 1 {container_type.__name__} exists so i assume the one you want is {choices[0][0]}")
        return choices[0][1]
    answer = inquirer.prompt([inquirer.List('c', message=message, choices=choices)])
    return answer['c']


def _select_server(message):
    return _select_container(message, Server)


def _select_client(message):
    return _select_container(message, Client)
