from ..util import docker_utils, storage
from ..inet.internet import Internet
from .printing import *

from itertools import count
import click
import inquirer

pass_inet = click.make_pass_decorator(Internet, ensure=True)
inet: Internet


@click.group()
@click.pass_context
def root(ctx):
    global inet
    inet = select_internet()
    ctx.call_on_close(lambda: storage.save_inet(inet))


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
    as_ = select_as('select as to create the server in: ')
    if as_ is None:
        print("You need to create an AS first")
        return

    current_names = [s.name for s in as_.list_servers()]
    default = gen_default_name(f'server{as_.asn}-', current_names)
    name = prompt_for_new_name("enter name for new server: ", existing_names=current_names, default=default)
    as_.create_server(name)


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


@rm.command("server")
@click.argument("srv_name", required=False)
def rm_server(srv_name):
    if srv_name is None:
        server = select_server("select server to remove: ")
    else:
        servers = inet.find_servers(srv_name)
        if len(servers) > 1:
            server = select_server("select server to remove: ")
        else:
            server = servers[0]
    server.as_.remove_server(server)


@root.group("ls")
def ls():
    pass


@ls.command("as")
def ls_as():
    print_as_table(inet.list_autonomous_systems())


@ls.command("servers")
def ls_servers():
    servers = [s for a in inet.list_autonomous_systems() for s in a.list_servers()]
    print_server_table(servers)


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


def select_as(message):
    choices = [(a.name, a) for a in inet.list_autonomous_systems()]
    if len(choices) == 0:
        return None
    elif len(choices) == 1:
        print("only one AS exists. I assume you want that one")
        return choices[0][1]
    answer = inquirer.prompt([inquirer.List('as', message=message, choices=choices)])
    as_ = answer['as']
    return as_


def select_server(message):
    choices = [(s.name, s) for s in inet.get_all_servers()]
    if len(choices) == 0:
        return None
    elif len(choices) == 1:
        print("only 1 server exists. i assume you want that one")
        return choices[0][1]
    answer = inquirer.prompt([inquirer.List('s', message=message, choices=choices)])
    return answer['s']
