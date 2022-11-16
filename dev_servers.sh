#!/bin/bash

echo "Lattice Local Development Script - params: ($1, $LATTICE_INI, $BUILDOUT)"

cd /app

if [ "$BUILDOUT" = "true" ];
then
    python3 -m venv lattice-venv
    . ./lattice-venv/bin/activate
    pip3 install -r requirements.txt
    buildout bootstrap
    bin/buildout

    if [ "$1" = "pserve" ];
    then
	npm install
    fi
else
    . ./lattice-venv/bin/activate
fi

export PATH=/usr/lib/postgresql/12/bin:/usr/share/elasticsearch/bin:$PATH

if [ "$1" = "pserve" ];
then
    ./bin/pserve --reload $LATTICE_INI
else
    ./bin/dev-servers $LATTICE_INI --app-name app --init --load --clear
fi
