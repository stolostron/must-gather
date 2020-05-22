#!/bin/bash
echo "BUILD GOES HERE!"

echo "<repo>/<component>:<tag> : $1"

export DOCKER_IMAGE_AND_TAG=${1}

make docker/build

