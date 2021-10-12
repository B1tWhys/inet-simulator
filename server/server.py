import socket, threading
from os import getenv
import logging as logging

logging.basicConfig(format=r'%(asctime)s %(ip)s|%(message)s', level=logging.DEBUG)

logging_context = {'ip': socket.gethostname()}

host = getenv('LISTEN_HOST', '')
port = int(getenv('PORT', '8000'))

def connection_worker(sock, client_addr):
    addr_str = ':'.join(str(x) for x in client_addr)
    logging.info(f"new connection from %s", addr_str, extra=logging_context)
    while True:
        data = sock.recv(1024);
        if not data: 
            logging.info("disconnecting from %s", addr_str, extra=logging_context)
            break
        logging.debug("echo (%s): %s", addr_str, data.decode('ascii').strip(), extra=logging_context)

with socket.create_server((host, port), reuse_port=True) as sock:
    while True:
        sock.listen()
        conn, addr = sock.accept()
        thread = threading.Thread(target=connection_worker, args=(conn, addr))
        thread.start()
