FROM python:3.10.6-bullseye

WORKDIR /app/

COPY ./requirements.txt /tmp/requirements.txt
COPY ./caraffabot /app/caraffabot

WORKDIR /tmp/

RUN apt-get update && apt-get upgrade -y

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

WORKDIR /app/