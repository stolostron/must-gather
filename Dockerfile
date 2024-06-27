# Copyright (c) 2021 Red Hat, Inc.
# Copyright Contributors to the Open Cluster Management project

FROM registry.access.redhat.com/openshift4/ose-cli:4.15

RUN microdnf update -y \
    && microdnf install -y tar rsync findutils gzip iproute util-linux wget \
    && microdnf clean all

RUN wget https://github.com/mikefarah/yq/releases/download/v4.44.2/yq_linux_amd64 -O /usr/bin/yq &&\
    chmod +x /usr/bin/yq

# copy all collection scripts to /usr/bin
COPY collection-scripts/* /usr/bin/

ENTRYPOINT /usr/bin/gather
