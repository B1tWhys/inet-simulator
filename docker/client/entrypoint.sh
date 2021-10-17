#!/bin/sh -e

/usr/local/bin/set_gateway "$GATEWAY_IP"

python3 client.py "$@"
