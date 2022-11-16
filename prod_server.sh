#!/bin/bash

echo "Lattice Production Startup Script - params: ($REBUILD, $CREATE_MAPPING)"

. ./lattice-venv/bin/activate

if [ "$REBUILD" = "true" ];
then
    bin/buildout buildout:es-ip=$ES_IP buildout:es-port=$ES_PORT buildout:pg-uri=$PG_URI
fi

if [ "$CREATE_MAPPING" = "true" ];
then
    ./bin/create-mapping production.ini --app-name app
fi

sudo service apache2 restart

tail -f /dev/null
