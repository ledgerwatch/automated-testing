#!/bin/bash

function stopContainers () {
    # stop containers
    echo "stopping containers..."
    docker compose --profile=first down -v --remove-orphans
    docker compose --profile=second down -v --remove-orphans
}

ORIGINAL_DIR=$(pwd)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "$SCRIPT_DIR" || exit

export DOCKER_UID=1000
export DOCKER_GID=1000

# set GITHUB_SHA
if [ -z "$GITHUB_SHA" ]; then
    export GITHUB_SHA=local
fi
echo "GITHUB_SHA=$GITHUB_SHA"

# set ERIGON_TAG
if [ -z "$ERIGON_TAG" ]; then
    export ERIGON_TAG=latest
fi
echo "ERIGON_TAG=$ERIGON_TAG"

export COMPOSE_PROJECT_NAME=automated-testing

# pull container images
echo "pulling container images..."
docker compose pull

# run node 1
echo "starting node 1..."
docker compose --profile=first up -d --force-recreate --remove-orphans

# wait for node 1 to start up
echo "waiting for node 1 to start up..."
sleep 10

# run node 2
echo "starting node 2..."
ENODE=$(./scripts/enode.sh) docker compose --profile=second up -d --force-recreate --remove-orphans

# wait for node 2 to start up
echo "waiting for node 2 to start up..."
sleep 10

# run tests!
echo "running tests..."
docker compose run --rm tests || { echo 'tests failed'; stopContainers; exit 1; }

stopContainers

cd "$ORIGINAL_DIR" || exit
