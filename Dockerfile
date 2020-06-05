#FROM quay.io/openshift/origin-cli:latest
FROM quay.io/openshift/origin-cli:4.5

# copy all collection scripts to /usr/bin
COPY collection-scripts/* /usr/bin/

ENTRYPOINT /usr/bin/gather
