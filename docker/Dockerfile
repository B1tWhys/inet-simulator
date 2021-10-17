FROM alpine

RUN apk add --update iptables python3 bash tcptraceroute iputils

ADD ./set_gateway /usr/local/bin
ADD ./server /server
ADD ./client /client
