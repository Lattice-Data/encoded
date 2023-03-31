#!/bin/bash

echo "Lattice Local Development Script - params: ($1, $LATTICE_INI, $BUILDOUT)"

cd /app

export PATH=/usr/lib/postgresql/11/bin:/usr/share/elasticsearch/bin:$PATH

if [ "$BUILDOUT" = "true" ];
then
    rm buildout_complete

    pip install -U setuptools
    pip3 install -r requirements.osx.txt
    buildout bootstrap

    touch buildout_complete

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
    echo "Waiting for buildout to complete..."
    until [ -f "buildout_complete" ]
    do
	sleep 5
    done
    ./bin/dev-servers $LATTICE_INI --app-name app --init --load --clear
fi
