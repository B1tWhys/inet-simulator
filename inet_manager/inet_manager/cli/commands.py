from ..util import docker_utils, storage
from ..inet.internet import Internet
from .printing import *

from itertools import count
import click
import inquirer

pass_inet = click.make_pass_decorator(Internet, ensure=True)


@click.group()
@click.pass_context
def root(ctx: click.Context):
    ctx.obj = select_internet()
    ctx.call_on_close(lambda: storage.save_inet(ctx.obj))


@root.group("docker")
def docker():
    pass


@docker.command("build")
def build():
    docker_utils.rebuild_imgs()


@root.group("new")
def new():
    pass


@new.command("as")
@click.argument("name", required=False)
@pass_inet
def new_as(inet: Internet, name: str):
    existing_names = {a.name for a in inet.list_autonomous_systems()}
    if not name:
        default_name = f"as-{inet.next_asn()}"
        name = prompt_for_new_name("enter name for new AS: ", existing_names, default=default_name)
    if name in existing_names:
        print(f"{name} already exists. Chose another name")
        return
    inet.create_as(name)


@new.command("server")
@pass_inet
def new_server(inet: Internet):
    as_ = select_as(inet, 'select as to create the server in: ')
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
@pass_inet
def rm_as(inet):
    choices = [(a.name, a) for a in inet.list_autonomous_systems()]
    if len(choices) == 0:
        print("There arent any as's to remove")
        return
    answer = inquirer.prompt([inquirer.List('as', message='select as to remove', choices=choices)])
    as_ = answer['as']
    inet.remove_as(as_)


@rm.command("server")
def rm_server():
    raise NotImplementedError()


@root.group("ls")
def ls():
    pass


@ls.command("as")
@pass_inet
def ls_as(inet: Internet):
    print_as_table(inet.list_autonomous_systems())


@ls.command("servers")
def ls_servers():
    raise NotImplementedError()


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


def select_as(inet, message):
    choices = [(a.name, a) for a in inet.list_autonomous_systems()]
    if len(choices) == 0:
        return None
    elif len(choices) == 1:
        print("only one AS exists. I assume you want that one")
        return choices[0][1]
    answer = inquirer.prompt([inquirer.List('as', message=message, choices=choices)])
    as_ = answer['as']
    return as_
