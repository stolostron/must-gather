#!/bin/bash
#set -x
# Copyright (c) 2021 Red Hat, Inc.
# Copyright Contributors to the Open Cluster Management project


BASE_COLLECTION_PATH="/must-gather"
mkdir -p ${BASE_COLLECTION_PATH}

HUB_CLUSTER=false
SPOKE_CLUSTER=false
MCE_NAME=""
OPERATOR_NAMESPACE=""
DEPLOYMENT_NAMESPACE=""

check_managed_clusters() {
    echo "The list of managed clusters that are configured on this Hub:" >> ${BASE_COLLECTION_PATH}/gather-managed.log
    #These calls will change with new API
    oc get managedclusters --all-namespaces >> ${BASE_COLLECTION_PATH}/gather-managed.log

    #to capture details in the managed cluster namespace to debug hive issues
    #refer https://github.com/open-cluster-management/backlog/issues/2682
    local mc_namespaces=$(oc get managedclusters --all-namespaces --no-headers=true -o custom-columns="NAMESPACE:.metadata.name")

    for mcns in ${mc_namespaces};
    do
        #oc kubectl get pods -n "$mcns" >> ${BASE_COLLECTION_PATH}/gather-managed.log
        oc adm inspect  ns/"$mcns"  --dest-dir=must-gather
    done
}

check_if_hub () {
    MCE_NAME=$(oc get multiclusterengines.multicluster.openshift.io --all-namespaces --no-headers=true | awk '{ print $1 }')
    echo "MCE name: $MCE_NAME"
    if [[ -n "$MCE_NAME" ]];
    then
      echo "This is a hub cluster"
      HUB_CLUSTER=true
      OPERATOR_NAMESPACE=$(oc get pod -l control-plane=backplane-operator --all-namespaces --no-headers=true | head -n 1 | awk '{ print $1 }')
      DEPLOYMENT_NAMESPACE=$(oc get mce "$MCE_NAME" -o jsonpath='{.spec.targetNamespace}')
    else
      echo "This is not a hub cluster, the above error can be safely ignored"
    fi
}

check_if_spoke () {
    if oc get crd clusterclaims.cluster.open-cluster-management.io;
    then
      echo "The current cluster has clusterclaims.cluster.open-cluster-management.io crd, it is a spoke cluster."
      SPOKE_CLUSTER=true
    else
      echo "The current cluster does not have clusterclaims.cluster.open-cluster-management.io crd, it is not a spoke cluster."
    fi
}

gather_spoke () {
    oc adm inspect klusterlets.operator.open-cluster-management.io --all-namespaces --dest-dir=must-gather
    oc adm inspect clusterclaims.cluster.open-cluster-management.io --all-namespaces  --dest-dir=must-gather

    KLUSTERLETS_NAMES=$(oc get klusterlets.operator.open-cluster-management.io --no-headers=true -o custom-columns="NAME:.metadata.name")
    for name in ${KLUSTERLETS_NAMES};
    do
      local agent_namespace
      local mode=$(oc get klusterlets.operator.open-cluster-management.io "$name" -o jsonpath='{.spec.deployOption.mode}')
      echo "klusterlet $name is deployed in $mode mode"
      if [ "$mode" = 'Hosted' ];
      then
        agent_namespace=$name
      else
        agent_namespace=$(oc get klusterlets.operator.open-cluster-management.io klusterlet -o jsonpath='{.spec.namespace}')
      fi

      echo "klusterlet name: $name, agent namespace: $agent_namespace"
      oc adm inspect ns/"$agent_namespace" --dest-dir=must-gather
      oc adm inspect ns/"${agent_namespace}-addon" --dest-dir=must-gather
    done

    oc adm inspect ns/openshift-operators --dest-dir=must-gather # gatekeeper operator will be installed in this ns in production
}

gather_hub() {
    check_managed_clusters
    oc get pods -n "${OPERATOR_NAMESPACE}" > ${BASE_COLLECTION_PATH}/gather-acm.log
    oc get pods -n "${DEPLOYMENT_NAMESPACE}" > ${BASE_COLLECTION_PATH}/gather-acm.log
    oc get csv -n "${OPERATOR_NAMESPACE}" > ${BASE_COLLECTION_PATH}/gather-acm.log
    oc adm inspect  ns/"${DEPLOYMENT_NAMESPACE}"  --dest-dir=must-gather
    oc adm inspect  ns/"${OPERATOR_NAMESPACE}"  --dest-dir=must-gather
    oc adm inspect  ns/open-cluster-management-hub  --dest-dir=must-gather
    # request from https://bugzilla.redhat.com/show_bug.cgi?id=1853485
    oc get proxy -o yaml > ${BASE_COLLECTION_PATH}/gather-proxy.log
    oc adm inspect  ns/hive  --dest-dir=must-gather
    oc adm inspect  multiclusterengines.multicluster.openshift.io --all-namespaces  --dest-dir=must-gather
    oc adm inspect hiveconfigs.hive.openshift.io --all-namespaces  --dest-dir=must-gather

    oc adm inspect clusterserviceversions.operators.coreos.com --all-namespaces  --dest-dir=must-gather
    oc adm inspect subscriptions.operators.coreos.com      --all-namespaces  --dest-dir=must-gather
    oc adm inspect installplans.operators.coreos.com --all-namespaces  --dest-dir=must-gather
    oc adm inspect operatorgroups.operators.coreos.com --all-namespaces  --dest-dir=must-gather

    oc adm inspect baremetalhosts.metal3.io --all-namespaces  --dest-dir=must-gather

    oc adm inspect placementdecisions.cluster.open-cluster-management.io --all-namespaces  --dest-dir=must-gather
    oc adm inspect placements.cluster.open-cluster-management.io --all-namespaces  --dest-dir=must-gather
    oc adm inspect clusterdeployments.hive.openshift.io --all-namespaces  --dest-dir=must-gather
    oc adm inspect syncsets.hive.openshift.io --all-namespaces --dest-dir=must-gather
    oc adm inspect clusterimagesets.hive.openshift.io --all-namespaces  --dest-dir=must-gather
    oc adm inspect machinesets.machine.openshift.io --all-namespaces  --dest-dir=must-gather
    oc adm inspect clustercurators.cluster.open-cluster-management.io --all-namespaces --dest-dir=must-gather

    oc adm inspect  managedclusterviews.view.open-cluster-management.io --all-namespaces  --dest-dir=must-gather
    oc adm inspect  managedclusteractions.action.open-cluster-management.io --all-namespaces  --dest-dir=must-gather
    oc adm inspect  manifestworks.work.open-cluster-management.io --all-namespaces  --dest-dir=must-gather
    oc adm inspect  managedclusters.cluster.open-cluster-management.io --all-namespaces  --dest-dir=must-gather
    oc adm inspect  managedclusterinfos.internal.open-cluster-management.io --all-namespaces  --dest-dir=must-gather
    oc adm inspect  clustermanagers.operator.open-cluster-management.io --all-namespaces  --dest-dir=must-gather
    oc adm inspect  managedserviceaccounts.authentication.open-cluster-management.io --all-namespaces  --dest-dir=must-gather


    oc adm inspect validatingwebhookconfigurations.admissionregistration.k8s.io --all-namespaces --dest-dir=must-gather
    oc adm inspect mutatingwebhookconfigurations.admissionregistration.k8s.io --all-namespaces --dest-dir=must-gather

    oc adm inspect  discoveredclusters.discovery.open-cluster-management.io --all-namespaces  --dest-dir=must-gather
    oc adm inspect  discoveryconfigs.discovery.open-cluster-management.io --all-namespaces  --dest-dir=must-gather

    oc adm inspect managedclusteraddons.addon.open-cluster-management.io  --all-namespaces  --dest-dir=must-gather

    oc adm inspect ns/openshift-monitoring  --dest-dir=must-gather

    # OpenShift console plug-in enablement
    oc adm inspect consoles.operator.openshift.io --dest-dir=must-gather
}

check_if_hub
check_if_spoke

if $HUB_CLUSTER;
then
  echo "Start to gather information for hub"
  gather_hub
fi

if $SPOKE_CLUSTER;
then
  echo "Start to gather information for spoke"
  gather_spoke
fi
