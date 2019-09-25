FROM node:10.16.3-stretch-slim

RUN apt-get update && apt-get install -y git python-pip
RUN pip install awscli==1.16.145 boto3 click

RUN mkdir tasks
COPY "./tasks/publish.sh" /tasks
