from prompt_toolkit import PromptSession, prompt
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.validation import Validator
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import traceback
from printing import *
from itertools import count

import docker_utils
import storage
from internet import Internet
import inquirer


class CLI:
    inet: Internet

    def __init__(self):
        self.commands = {
            'docker': {
                'build': self.rebuild_docker
            },
            'rm': {
                'as': self.remove_as
            },
            'new': {
                'internet': self.create_internet,
                'as': self.create_as
            },
            'ls': {
                'as': self.list_autonomous_systems,
            },
            'save': self.save_inet
        }

        self.save_required = False
        completion_dict = self.__build_completion_dict()
        self.select_internet()
        self.save_inet(None)
        self.session = PromptSession(lambda: f"[{self.inet.name}] > ", vi_mode=True,
                                     history=storage.get_prompt_history(),
                                     completer=NestedCompleter.from_nested_dict(completion_dict),
                                     auto_suggest=AutoSuggestFromHistory())

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
                self._eval(cmd)
                self.save_inet(None)
            except KeyboardInterrupt:
                return
            except Exception:
                traceback.print_exc()

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

    #############
    # Command handlers
    #############

    def delete_containers(self, _):
        raise NotImplementedError()

    def create_as(self, _):
        existing_names = {a.name for a in self.inet.get_autonomous_systems()}
        default_name = f"as-{self.inet.next_asn()}"
        name = self.prompt_for_new_name("enter name for new AS: ", existing_names, default=default_name)
        self.inet.create_as(name)

    def remove_as(self, as_name):
        if not as_name:
            choices = [(a.name, a) for a in self.inet.get_autonomous_systems()]
            if len(choices) == 0:
                print("There arent any as's to remove")
                return
            answer = inquirer.prompt([inquirer.List('as', message='select as to remove', choices=choices)])
            as_ = answer['as']
        else:
            as_ = next(filter(lambda a: a.name == as_name, self.inet.get_autonomous_systems()))
        self.inet.remove_as(as_)

    def list_autonomous_systems(self, _):
        print_as_table(self.inet.get_autonomous_systems())

    def rebuild_docker(self, _):
        docker_utils.rebuild_imgs()

    def create_internet(self, _):
        existing_names = storage.get_saved_inet_names()
        default_name = self.gen_default_name('inet-', existing_names)
        name = self.prompt_for_new_name(f"enter name for new internet: ", existing_names, default=default_name)
        self.inet = Internet(name=name)

    def select_internet(self):
        inet_names = storage.get_saved_inet_names()
        if len(inet_names) == 0:
            self.create_internet(None)
        elif len(inet_names) == 1:
            self.inet = storage.load_inet(inet_names[0])
        else:
            answer = inquirer.prompt([inquirer.List('inet_name',
                                                    message="select internet to operate on",
                                                    choices=inet_names)])
            self.inet = storage.load_inet(answer['inet_name'])

    def save_inet(self, _):
        storage.save_inet(self.inet)

    @staticmethod
    def prompt_for_new_name(message, existing_names, *args, **kwargs):
        validator = Validator.from_callable(lambda n: n not in existing_names,
                                            error_message='That name is already taken')
        return prompt(message, validator=validator, validate_while_typing=True, *args, **kwargs)

    @staticmethod
    def gen_default_name(prefix, existing_names):
        for i in count(1):
            name = prefix + str(i)
            if name not in existing_names:
                return name


if __name__ == '__main__':
    cli = CLI()
    cli.run()
