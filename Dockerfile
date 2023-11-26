# Use an official Python runtime as the base image
FROM ubuntu:latest

# Set the working directory in the container
WORKDIR /usr/src/rh 

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependency
RUN \
  sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list && \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y build-essential && \
  apt-get install -y software-properties-common && \
  apt-get install -y byobu curl git htop man unzip vim wget && \
  apt-get install -y python3 python3-pip python3.10-dev libmysqlclient-dev
  
  # rm -rf /var/lib/apt/lists/*

# Install NodeJs - Install the latest version
# RUN apt-get install nodejs

RUN apt-get install -y pkg-config cmake-data libpq-dev

RUN pip install virtualenvwrapper poetry psycopg2-binary

# Copy project files
COPY ["README.md", "Makefile", "poetry.lock","pyproject.toml","/usr/src/rh/"]
COPY ./src /usr/src/rh/src

# Copy and install Python dependencies
RUN poetry install --no-root

# Expose port 8000
EXPOSE 8000

# Set up the entrypoint
COPY ./scripts/entrypoint.sh /usr/src/rh/entrypoint.sh
RUN chmod a+x /usr/src/rh/entrypoint.sh
# this executed as soon as the image is up
ENTRYPOINT ["/usr/src/rh/entrypoint.sh"]
