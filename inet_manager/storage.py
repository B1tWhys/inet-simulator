from appdirs import user_data_dir
import yaml
from internet import Internet
from os import makedirs
from os.path import join, exists
from dacite import from_dict

app_name = 'inet_manager'
data_dir = user_data_dir(appname=app_name)
state_file_path = join(data_dir, 'state.yaml')
makedirs(data_dir, exist_ok=True)

print(state_file_path)


def save_inet(inet: Internet):
    state = load_state()
    state[inet.name] = inet
    with open(state_file_path, 'w') as f:
        yaml.dump(state, f)


def load_inet(inet_name: str) -> Internet:
    state = load_state()
    if inet_name not in state:
        raise KeyError(f"Internet {inet_name} does not exist!")
    else:
        return state[inet_name]


def get_saved_inet_names():
    return [k for k in load_state().keys()]


def load_state() -> dict:
    if not exists(state_file_path):
        return {}

    with open(state_file_path, 'r') as f:
        return yaml.load(f, Loader=yaml.Loader)
