from tabulate import tabulate
from ..inet.autonomous_system import AS
from ..inet.containers import SingleInterfaceContainer
from dataclasses import asdict


def print_as_table(as_list: list[AS]):
    records = []
    for as_ in as_list:
        a_d = asdict(as_)
        record = {k: a_d[k] for k in ['name', 'asn', 'subnet', 'docker_network_id']}
        records.append(record)
    print(tabulate(records, headers='keys'))


def print_single_interface_container_table(container_list: list[SingleInterfaceContainer]):
    records = []
    for c in container_list:
        record = {'Name': c.name,
                  'Container id': c.container_id,
                  'IP': c.ip,
                  'AS name': c.as_name}
        records.append(record)
    print(tabulate(records, headers='keys'))
