# Copyright (c) 2021 Red Hat, Inc.
# Copyright Contributors to the Open Cluster Management project

FROM quay.io/openshift/origin-cli:4.16 as builder

RUN wget https://github.com/mikefarah/yq/releases/download/v4.44.2/yq_linux_amd64 -O /usr/bin/yq && \
    chmod +x /usr/bin/yq

FROM registry.access.redhat.com/ubi9/ubi-minimal:latest

ENV BASE_COLLECTION_PATH=/must-gather \
    USER_UID=1001 \
    USER_NAME=must-gather

RUN microdnf update -y \
    && microdnf install -y rsync findutils \
    && microdnf clean all

# Copy binaries
COPY --from=builder /usr/bin/oc /usr/bin/oc
COPY --from=builder /usr/bin/yq /usr/bin/yq

# copy all collection scripts to /usr/bin
COPY collection-scripts/* /usr/bin/

# Setup non-root user
COPY build/user_setup /usr/local/bin/
RUN  /usr/local/bin/user_setup
USER 1001

ENTRYPOINT /usr/bin/gather
