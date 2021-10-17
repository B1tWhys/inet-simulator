from tabulate import tabulate
from autonomous_system import AS
from dataclasses import asdict


def print_as_table(as_list: list[AS]):
    print(tabulate([asdict(as_) for as_ in as_list], headers='keys'))
