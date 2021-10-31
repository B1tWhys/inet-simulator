from tabulate import tabulate
from ..inet.autonomous_system import AS
from ..inet.server import Server
from ..inet.client import Client
from dataclasses import asdict
from typing import Union


def print_as_table(as_list: list[AS]):
    records = []
    for as_ in as_list:
        a_d = asdict(as_)
        record = {k: a_d[k] for k in ['name', 'asn', 'subnet', 'docker_network_id']}
        records.append(record)
    print(tabulate(records, headers='keys'))


def print_container_table(container_list: list[Union[Server, Client]]):
    records = []
    for c in container_list:
        c_d = asdict(c)
        record = c_d
        record['as'] = c.as_.name
        record['asn'] = c.as_.asn
        record = {k: record[k] for k in ['name', 'as', 'asn', 'ip']}
        records.append(record)
    print(tabulate(records, headers='keys'))
