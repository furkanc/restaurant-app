# Use an official Python runtime as a parent image
FROM python:3.11.6-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Set the working directory
WORKDIR /app

# Install dependencies
COPY ./requirements.txt /tmp

RUN apt-get update && apt-get --no-install-recommends install -y \
  vim \
  build-essential \
  pkg-config \
  default-libmysqlclient-dev \
  && rm -rf /var/lib/apt/lists/* \
  && python -m pip install --upgrade pip \
  && pip install -r /tmp/requirements.txt
