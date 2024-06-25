# Copyright (c) 2021 Red Hat, Inc.
# Copyright Contributors to the Open Cluster Management project

FROM quay.io/openshift/origin-cli:4.16 as builder

FROM registry.access.redhat.com/ubi8/ubi-minimal:latest

RUN microdnf update -y \
    && microdnf install -y tar rsync findutils gzip iproute util-linux wget \
    && microdnf clean all

RUN wget https://github.com/mikefarah/yq/releases/download/v4.2.0/yq_linux_amd64 -O /usr/bin/yq &&\
    chmod +x /usr/bin/yq

# Copy oc binary
COPY --from=builder /usr/bin/oc /usr/bin/oc

# copy all collection scripts to /usr/bin
COPY collection-scripts/* /usr/bin/

ENTRYPOINT /usr/bin/gather
