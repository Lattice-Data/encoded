#!/bin/bash

echo "Lattice Local Development Script - params: ($1, $LATTICE_INI, $BUILDOUT)"

cd /app

export PATH=/usr/lib/postgresql/12/bin:/usr/share/elasticsearch/bin:$PATH

if [ "$BUILDOUT" = "true" ];
then
    pip install -U setuptools
    pip3 install -r requirements.osx.txt
    buildout bootstrap
    bin/buildout

    if [ "$1" = "pserve" ];
    then
	npm install
    fi
fi

if [ "$1" = "pserve" ];
then
    ./bin/pserve --reload $LATTICE_INI
else
    ./bin/dev-servers $LATTICE_INI --app-name app --init --load --clear
fi
