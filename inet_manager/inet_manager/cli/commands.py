from ..util import docker_utils, storage
from ..inet.internet import Internet

from itertools import count
import click
import inquirer

pass_inet = click.make_pass_decorator(Internet, ensure=True)


@click.group()
@click.pass_context
def root(ctx):
    ctx.obj = select_internet()


@root.command("save")
@pass_inet
def save(inet):
    storage.save_inet(inet)


@root.group("docker")
def docker():
    pass


@docker.command("build")
def build():
    docker_utils.rebuild_imgs()


@root.group("new")
def new():
    pass


@new.command("internet")
def new_internet():
    raise NotImplementedError()


@new.command("server")
def new_server():
    raise NotImplementedError()


@new.command("as")
def new_server():
    raise NotImplementedError()


@new.command("router")
def new_router():
    raise NotImplementedError()


@root.group("rm")
def rm():
    pass


@rm.command("as")
def rm_as():
    raise NotImplementedError()


@rm.command("server")
def rm_server():
    raise NotImplementedError()


@root.group("ls")
def ls():
    pass


@ls.command("as")
def ls_as():
    raise NotImplementedError()


@ls.command("servers")
def ls_servers():
    raise NotImplementedError()


def prompt_for_new_name(message, existing_names, default=""):
    return "placeholder name"


def gen_default_name(prefix, existing_names):
    for i in count(1):
        name = prefix + str(i)
        if name not in existing_names:
            return name


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


def create_internet():
    existing_names = storage.get_saved_inet_names()
    default_name = gen_default_name('inet-', existing_names)
    name = prompt_for_new_name(f"enter name for new internet: ", existing_names, default=default_name)
    return Internet(name=name)
