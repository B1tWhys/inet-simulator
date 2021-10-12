#!/bin/bash -x

docker build -t bgp-client . && docker run --network bgp-test-1 --rm bgp-client -H $1 -p 8000
