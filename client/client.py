import socket
import logging
import argparse
from time import sleep

logging.basicConfig(format=r'%(asctime)s %(host)s %(ip)s|%(message)s', level=logging.DEBUG)
client_host = socket.gethostname()
client_ip = socket.gethostbyname(client_host)
log_context = {'host': client_host, 'ip': client_ip}

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', dest='host')
parser.add_argument('-p', '--port', dest='port', type=int, default=8000)
args = parser.parse_args()

host = args.host
port = args.port

logging.info("starting ping requests", extra=log_context)
with socket.create_connection((host, port)) as sock:
    while True:
        msg = f"ping from {client_ip}"
        logging.info("sending to %s: %s", host, msg, extra=log_context)
        sock.send(msg.encode('ascii'))
        resp = sock.recv(1024)
        logging.info("received from %s: %s", host, resp.decode('ascii').strip(), extra=log_context)
        sleep(1)
