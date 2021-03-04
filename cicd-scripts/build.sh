#!/bin/bash
# Copyright (c) 2021 Red Hat, Inc.
# Copyright Contributors to the Open Cluster Management project
echo "BUILD GOES HERE!"

echo "<repo>/<component>:<tag> : $1"

export DOCKER_IMAGE_AND_TAG=${1}

make docker/build

