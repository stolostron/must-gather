#!/bin/bash
#set -x
# Copyright (c) 2021 Red Hat, Inc.
# Copyright Contributors to the Open Cluster Management project


BASE_COLLECTION_PATH="/must-gather"
mkdir -p ${BASE_COLLECTION_PATH}

CLUSTER="SPOKE"
MCE_NAME=""
MCNAMESPACE=""
OPERATORNAMESPACE=""

check_managed_clusters() {
    echo "The list of managed clusters that are configured on this Hub:" >> ${BASE_COLLECTION_PATH}/gather-managed.log
    #These calls will change with new API
    oc get managedclusters --all-namespaces >> ${BASE_COLLECTION_PATH}/gather-managed.log
    
    #to capture details in the managed cluster namespace to debug hive issues
    #refer https://github.com/open-cluster-management/backlog/issues/2682
    MCNAMESPACE=`oc get managedclusters --all-namespaces --no-headers=true -o custom-columns="NAMESPACE:.metadata.name"`
    
    for mcns in ${MCNAMESPACE[@]};
    do
        #oc kubectl get pods -n "$mcns" >> ${BASE_COLLECTION_PATH}/gather-managed.log
        oc adm inspect  ns/"$mcns"  --dest-dir=must-gather
    done

}

check_if_hub () {
    MCE_NAME=`oc get multiclusterengines.multicluster.openshift.io --all-namespaces --no-headers=true | awk '{ print $1 }'`
    echo "$MCE_NAME"
     if [[ -z "$MCE_NAME" ]] ;
        then 
        echo "If the cluster is a managed cluster, the above error can be safely ignored"
        CLUSTER="SPOKE"
     else  
        CLUSTER="HUB"
        OPERATORNAMESPACE="`oc get pod -l control-plane=backplane-operator --all-namespaces --no-headers=true | head -n 1 | awk '{ print $1 }'`"
        DEPLOYMENTNAMESPACE="`oc get mce $MCE_NAME -o jsonpath='{.spec.targetNamespace}'`"
     fi 
}

gather_spoke () {


    oc adm inspect klusterlets.operator.open-cluster-management.io --all-namespaces  --dest-dir=must-gather
    oc adm inspect clusterclaims.cluster.open-cluster-management.io --all-namespaces  --dest-dir=must-gather
    oc adm inspect ns/open-cluster-management-agent --dest-dir=must-gather
    oc adm inspect ns/open-cluster-management-agent-addon --dest-dir=must-gather

    oc adm inspect ns/openshift-operators --dest-dir=must-gather # gatekeeper operator will be installed in this ns in production
}

check_if_hub

echo "$CLUSTER"

case "$CLUSTER" in 
    #case 1 
    "HUB")

    check_managed_clusters
    oc get pods -n "${OPERATORNAMESPACE}" > ${BASE_COLLECTION_PATH}/gather-acm.log
    oc get pods -n "${DEPLOYMENTNAMESPACE}" > ${BASE_COLLECTION_PATH}/gather-acm.log
    oc get csv -n "${OPERATORNAMESPACE}" > ${BASE_COLLECTION_PATH}/gather-acm.log
    oc adm inspect  ns/"${DEPLOYMENTNAMESPACE}"  --dest-dir=must-gather
    oc adm inspect  ns/"${OPERATORNAMESPACE}"  --dest-dir=must-gather
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

    oc adm inspect baremetalassets.inventory.open-cluster-management.io --all-namespaces  --dest-dir=must-gather
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
    ;;

      
    #case 2 
    "SPOKE")
    gather_spoke
    ;; 
      
   
esac 
