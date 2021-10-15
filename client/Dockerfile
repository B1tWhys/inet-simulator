FROM python:3.9.7-alpine

RUN apk add iptables

ADD ./client.py .

ENTRYPOINT ["python3", "./client.py"]
