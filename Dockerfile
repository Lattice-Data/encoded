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

# Install Conda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh -O ~/miniconda.sh && /bin/bash ~/miniconda.sh -b -p /opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

WORKDIR /app

RUN useradd -m --groups sudo latticed && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    chown -R latticed /var/log/nginx /var/lib/nginx && \
    mkdir -p /run && chown -R latticed /run

CMD git config --global --add safe.directory /app


FROM base AS dev_servers

RUN wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.6.16.deb && \
    dpkg -i elasticsearch-5.6.16.deb && rm elasticsearch-5.6.16.deb && \
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg && \
    echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" | tee /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && apt-get install -y postgresql-11 && rm -rf /var/lib/apt/lists/*

RUN sed -i '$d' /etc/java-11-openjdk/security/java.policy && sed -i "$ a permission javax.management.MBeanTrustPermission \"register\";" /etc/java-11-openjdk/security/java.policy && sed -i "$ a };" /etc/java-11-openjdk/security/java.policy

USER latticed

ENV PATH=/usr/lib/postgresql/11/bin:/usr/share/elasticsearch/bin:$PATH

RUN conda create --name lattice_env python=3.7 && \
    conda config --append channels conda-forge && \
    conda install -n lattice_env -c anaconda psycopg2==2.8.4

CMD echo "In the container's terminal, run:\n> /bin/bash dev_servers.sh \"dev-servers\"" && tail -f /dev/null


FROM base as pserve

USER latticed

RUN conda create --name lattice_env python=3.7 && \
    conda config --append channels conda-forge && \
    conda install -n lattice_env -c anaconda psycopg2==2.8.4

ENV PATH=/usr/lib/postgresql/12/bin:/usr/share/elasticsearch/bin:$PATH

CMD conda run --no-capture-output -n lattice_env /bin/bash dev_servers.sh "pserve"
