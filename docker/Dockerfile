FROM alpine

RUN apk add --update iptables python3 bash tcptraceroute iputils tcpdump

ADD bashrc /root/.bashrc
ADD ./set_gateway /usr/local/bin
ADD ./server /server
ADD ./client /client
