FROM ubuntu:20.04 AS base
# Ubuntu 20 is the last compatible version for node@10

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    sudo \
    g++ \
    wget \
    curl \
    git \
    python2 \
    ruby \
    ruby-dev \
    libffi-dev \
    libbz2-dev \
    libpq-dev \
    libyaml-cpp-dev \
    libyaml-dev \
    libarchive-tools \
    libssl-dev \
    openssl \
    zlib1g-dev \
    zlib1g \
    libjpeg-dev \
    tk-dev \
    tcl-dev \
    uuid-dev \
    lzma-dev \
    liblzma-dev \
    default-jre \
    default-jdk \
    apt-transport-https \
    nginx \
    libmagic-dev \
    graphviz \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sL https://deb.nodesource.com/setup_10.x | bash - && apt-get install -y nodejs \
    && gem install compass

# Install Python 3.7.6
RUN wget https://www.python.org/ftp/python/3.7.6/Python-3.7.6.tgz && \
    tar xzvf Python-3.7.6.tgz && \
    cd Python-3.7.6 && \
    ./configure && \
    make && \
    make install && \
    cd .. && rm -r Python-3.7.6.tgz Python-3.7.6/

WORKDIR /app

RUN useradd -m --groups sudo latticed && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    chown -R latticed /var/log/nginx /var/lib/nginx && \
    mkdir -p /run && chown -R latticed /run

COPY --chown=latticed ./dev_servers.sh /usr/local/bin
RUN chmod +x /usr/local/bin/dev_servers.sh

CMD git config --global --add safe.directory /app


FROM base AS dev_servers

RUN wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.6.16.deb && \
    dpkg -i elasticsearch-5.6.16.deb && rm elasticsearch-5.6.16.deb && \
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg && \
    echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" | tee /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && apt-get install -y postgresql-12 && rm -rf /var/lib/apt/lists/*

USER latticed

CMD exec dev_servers.sh "dev-servers"


FROM base as pserve

CMD exec dev_servers.sh "pserve"
