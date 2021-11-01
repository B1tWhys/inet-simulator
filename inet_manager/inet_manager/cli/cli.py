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
    inet = select_internet()
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
        name = prompt_for_new_name("enter name for new AS: ", existing_names, default=default_name)
    if name in existing_names:
        print(f"{name} already exists. Chose another name")
        return
    inet.create_as(name)


@new.command("server")
def new_server():
    as_ = select_as('select AS to create the server in:')
    if as_ is None:
        print("You need to create an AS first")
        return

    current_names = [s.name for s in inet.list_containers(Server)]
    default = gen_default_name(f'server{as_.asn}-', current_names)
    name = prompt_for_new_name("enter name for new server: ", existing_names=current_names, default=default)
    inet.create_server(name, as_)


@new.command("client")
def new_client():
    as_ = select_as('select AS to create client in:')
    if as_ is None:
        print("You need to create an AS first")
        return
    current_names = [s.name for s in inet.list_containers(Client)]
    server = select_server('select server for client to make requests to')
    if server is None:
        print("No servers exist for the client to make requests to. Create a server first!")
        exit(1)
    default = gen_default_name(f'client{as_.asn}-', current_names)
    name = prompt_for_new_name("enter name for new client: ", existing_names=current_names, default=default)
    inet.create_client(name, as_, server)


@new.command("router")
def new_router():
    raise NotImplementedError()


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


@rm.command("container")
@click.argument("container_name", required=False)
def rm_container(srv_name):
    if srv_name is None:
        container = select_server("select container to remove: ")
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
        client = select_client("Select client to remove: ")
    else:
        client = inet.find_client(client_name)
        if client is None:
            print(f"Client {client} not found!")
            exit(1)
    inet.remove_container(client)


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


def prompt_for_new_name(message, existing_names, default=None):
    return inquirer.text(message=message, validate=lambda c, m: m not in existing_names, default=default)


def gen_default_name(prefix, existing_names):
    for i in count(1):
        name = prefix + str(i)
        if name not in existing_names:
            return name


def create_internet():
    existing_names = storage.get_saved_inet_names()
    default_name = gen_default_name('inet-', existing_names)
    name = prompt_for_new_name("enter name for new internet", existing_names, default=default_name)
    return Internet(name=name)


def select_internet():
    inet_names = storage.get_saved_inet_names()
    if len(inet_names) == 0:
        return create_internet()
    elif len(inet_names) == 1:
        return storage.load_inet(inet_names[0])
    else:
        answer = inquirer.prompt([inquirer.List('inet_name',
                                                message="select internet to operate on",
                                                choices=inet_names)])
        return storage.load_inet(answer['inet_name'])


def select_as(message) -> Union[AS, None]:
    choices = [(a.name, a) for a in inet.list_autonomous_systems()]
    if len(choices) == 0:
        return None
    elif len(choices) == 1:
        print(f"only one AS exists so I assume the one you want is {choices[0][0]}")
        return choices[0][1]
    answer = inquirer.prompt([inquirer.List('as', message=message, choices=choices)])
    as_ = answer['as']
    return as_


def select_container(message, container_type):
    choices = [(c.name, c) for c in inet.list_containers(container_type=container_type)]
    if len(choices) == 0:
        return None
    elif len(choices) == 1:
        print(f"Only 1 {container_type.__name__} exists so i assume the one you want is {choices[0][0]}")
        return choices[0][1]
    answer = inquirer.prompt([inquirer.List('c', message=message, choices=choices)])
    return answer['c']


def select_server(message):
    return select_container(message, Server)
    # choices = [(s.name, s) for s in inet.get_all_servers()]
    # if len(choices) == 0:
    #     return None
    # elif len(choices) == 1:
    #     print(f"Only 1 server exists so i assume the one you want is {choices[0][0]}")
    #     return choices[0][1]
    # answer = inquirer.prompt([inquirer.List('s', message=message, choices=choices)])
    # return answer['s']


def select_client(message):
    return select_container(message, Client)
    # choices = [(c.name, c) for c in inet.get_all_clients()]
    # if len(choices) == 0:
    #     return None
    # elif len(choices) == 1:
    #     print(f"Only 1 client exists so I assume the one you want {choices[0][0]}")
    #     return choices[0][1]
    # answer = inquirer.prompt([inquirer.List('c', message=message, choices=choices)])
    # return answer['c']
