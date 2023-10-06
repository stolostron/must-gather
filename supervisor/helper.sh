#!/bin/bash
set -x
# Function to display script usage
display_usage() {
    #echo "Usage: $0 <cluster_url> <username> <password>"
    echo "Usage: $0 <cluster_url> <token>"
    exit 1
}

# Check if the required number of arguments are provided
#if [ "$#" -ne 2 ]; then
#    display_usage
#fi

# Assign command-line arguments to variables
#OC_CLUSTER_URL="$1"
#OC_TOKEN="$2"
#OC_USERNAME="$2"
#OC_PASSWORD="$3"

# Log in to the OpenShift cluster
#oc login "$OC_CLUSTER_URL" -u "$OC_USERNAME" -p "$OC_PASSWORD"
#oc login "$OC_CLUSTER_URL" --token "$OC_TOKEN" --insecure-skip-tls-verify=true
oc login ${OC_CLUSTER_URL} --token ${OC_TOKEN} --insecure-skip-tls-verify=true

#python ~/code/acm-inspector/src/supervisor/entry.py prom
cd /acm-inspector/src/supervisor
python entry.py prom



