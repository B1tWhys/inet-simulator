from tabulate import tabulate
from autonomous_system import AS
from server import Server
from dataclasses import asdict


def print_as_table(as_list: list[AS]):
    records = []
    for as_ in as_list:
        a_d = asdict(as_)
        record = {k: a_d[k] for k in ['name', 'asn', 'subnet', 'docker_network_id']}
        records.append(record)
    print(tabulate(records, headers='keys'))


def print_server_table(srv_list: list[Server]):
    records = []
    for s in srv_list:
        s_d = asdict(s)
        record = s_d
        record['as'] = s.as_.name
        record['asn'] = s.as_.asn
        records.append(record)
    print(tabulate(records, headers='keys'))
