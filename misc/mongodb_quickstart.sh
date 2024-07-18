#!/bin/bash
# MongoDB quick-start script provided for skelet0wn framework
# Please be aware this container will not persist its data upon stopping

lscpu | grep -q "avx"

if [[ $? -ne 0 ]]; then
    echo "No AVX support found in CPU configuration, falling back to non-official MongoDB docker image"
    export IMAGE="nertworkweb/mongodb-no-avx"
else
    echo "AVX support OK, using official MongoDB docker image"
    export IMAGE="mongo"
fi

echo "Starting docker container:"
docker run --rm --name mongodb -p 27017:27017 -d $IMAGE:latest --bind_ip_all

