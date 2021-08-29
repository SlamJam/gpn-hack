#!/bin/bash

set -e

cd $(dirname $(realpath $0))

echo "Work dir:" $(pwd)

pushd .. > /dev/null

docker-compose pull
docker-compose up -d --remove-orphans

docker container prune --force
docker image prune --force

