from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text as print
import traceback

import docker_utils


class CLI:
    def __init__(self):
        self.commands = {
            'delete': {
                'all': self.delete_containers
            },
            'ls': {
                'containers': self.list_containers
            }
        }
        self.session = PromptSession('> ', vi_mode=True)

    def run(self):
        while True:
            try:
                cmd = self.session.prompt()
                self.eval(cmd)
            except KeyboardInterrupt:
                return
            except Exception:
                traceback.print_exc()

    def delete_containers(self, _):
        print("deleting everything")

    def list_containers(self, _):
        print(docker_utils.get_containers())

    def eval(self, cmd, tree=None):
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
                    self.eval(cmd_parts[1], tree=handler)
        else:
            print(f"invalid command: {cmd}")


if __name__ == '__main__':
    cli = CLI()
    cli.run()
