from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.completion import NestedCompleter
import traceback
import importlib
import inquirer

import docker_utils
import storage
from internet import Internet


def reload():
    mods = [docker_utils]
    for mod in mods:
        importlib.reload(mod)


class CLI:
    inet: Internet

    def __init__(self):
        self.commands = {
            'docker': {
                'build': self.rebuild_docker
            },
            'rm': {
                'all': self.delete_containers
            },
            'new': {
                'internet': self.create_internet,
                'as': self.create_as
            },
            'ls': {
                'autonomous-systems': self.list_ASes,
                'containers': self.list_containers
            },
            'save': self.save_inet
        }
        self.save_required = False
        completion_dict = self.__build_completion_dict()
        self.select_internet()
        self.save_inet(None)
        self.session = PromptSession(lambda: f"[{self.inet.name}] > ", vi_mode=True, completer=NestedCompleter.from_nested_dict(completion_dict))

    def __build_completion_dict(self, tree_root=None):
        if tree_root is None:
            tree_root = self.commands
        ret = {}
        for k, v in tree_root.items():
            if callable(v):
                ret[k] = None
            else:
                ret[k] = self.__build_completion_dict(tree_root=v)
        return ret

    def run(self):
        while True:
            try:
                cmd = self.session.prompt()
                self.save_inet(None)
                reload()
                self._eval(cmd)
            except KeyboardInterrupt:
                return
            except Exception:
                traceback.print_exc()

    def delete_containers(self, _):
        raise NotImplementedError()

    def list_containers(self, _):
        raise NotImplementedError()

    def list_ASes(self, _):
        raise NotImplementedError()

    def create_as(self, _):
        raise NotImplementedError()

    def rebuild_docker(self, _):
        docker_utils.rebuild_imgs()

    def create_internet(self, _):
        num_existing = len(storage.get_saved_inet_names())
        default_name = f"inet-{num_existing + 1}"
        questions = [inquirer.Text('name', message='enter name for new internet', default=default_name)]
        answers = inquirer.prompt(questions)
        self.inet = Internet(name=answers['name'])

    def select_internet(self):
        inet_names = storage.get_saved_inet_names()
        if len(inet_names) == 0:
            self.create_internet(None)
        elif len(inet_names) == 1:
            self.inet = storage.load_inet(inet_names[0])
        else:
            answer = inquirer.prompt([inquirer.List('inet_name', choices=inet_names)])
            self.inet = storage.load_inet(answer.inet_name[0])

    def save_inet(self, _):
        storage.save_inet(self.inet)

    def _eval(self, cmd, tree=None):
        if tree is None:
            tree = self.commands
        if cmd.strip() == '':
            return

        cmd_parts = cmd.strip().split(' ', 1)
        if len(cmd_parts) == 0:
            return

        if cmd_parts[0] in tree:
            handler = tree[cmd_parts[0]]
            if callable(handler):
                arg = cmd_parts[1] if len(cmd_parts) > 1 else None
                handler(arg)
            elif isinstance(handler, dict):
                if len(cmd_parts) == 1:
                    print("incomplete command")
                else:
                    self._eval(cmd_parts[1], tree=handler)
        else:
            print(f"invalid command: {cmd}")


if __name__ == '__main__':
    cli = CLI()
    cli.run()
