import os
import errno
import socket
from pathlib import Path


path = Path(__file__).parent.absolute()


def check_ports(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            print(f"Port {port} is already in use. Checking port {port + 1}")
            port = check_ports(port + 1)
        else:
            # something else raised the socket.error exception
            print(e)

    s.close()
    return port


port = check_ports(5000)
bind = f"0.0.0.0:{port}"

workers = 1

accesslog = os.path.join(path, 'logs/access-logs.log')
errorlog = os.path.join(path, 'logs/debug-logs.log')

loglevel = 'debug'
capture_output = True

worker_class = 'gthread'
keep_alive = 300
timeout = 300
