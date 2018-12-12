FROM python:3.7

MAINTAINER  Vassiliy Vorobyov <vv@pwrg.ru>

ENV PYTHONUNBUFFERED 1

RUN apt update
RUN apt install -y --no-install-recommends software-properties-common libnewlib-arm-none-eabi avr-libc git unzip build-essential python-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install cryptography
COPY . /code
COPY requirements.txt /code/requirements.txt
WORKDIR /code
RUN pip install cython
RUN pip install -r /code/requirements.txt
RUN ldconfig