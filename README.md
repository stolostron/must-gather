# must-gather script for ACM

This is experimental right now. 

## Usage

```sh
oc adm must-gather --image=quay.io/open-cluster-management/must-gather:0.1.0-SNAPSHOT-2020-06-....
```

If you need the results to be saved in a named directory, then following the must-gather instructions, this can be run:

```sh
oc adm must-gather --image=quay.io/open-cluster-management/must-gather:0.1.0-SNAPSHOT-2020-06-.... --dest-dir=SOMENAME ; tar -cvzf SOMENAME.tgz SOMENAME
```

In addition, if we need to collect must-gather for the OpenShift infrastructure, we can run:
```
oc adm must-gather
```

## Information Captured
1. The above must-gather command can understand where it is being run - ACM Hub Server or Managed (Spoke) Cluster and collects data accordingly.
2. If run on the ACM Hub Server, it will also capture a list of Spoke Clusters configured and the status. This is found in the `gather-spoke.log` If a Spoke Cluster reports a status of not equal to Ready when it is expected to be, then the must-gather command above should be run on the Spoke Cluster as well.

### If run on ACM Hub, it collects (is being updated soon to match New APIs):

- oc adm inspect  ns/open-cluster-management
- oc adm inspect  ns/hive 
- oc adm inspect  multiclusterhubs.operators.open-cluster-management.io --all-namespaces
- oc adm inspect endpointconfigs.multicloud.ibm.com --all-namespaces
- oc adm inspect  hiveconfigs.hive.openshift.io --all-namespaces 
- oc adm inspect  applications.app.k8s.io --all-namespaces 
- oc adm inspect  channels.apps.open-cluster-management.io --all-namespaces
- oc adm inspect  deployables.apps.open-cluster-management.io --all-namespaces
- oc adm inspect  placementrules.apps.open-cluster-management.io --all-namespaces
- oc adm inspect  subscriptions.apps.open-cluster-management.io --all-namespaces
- oc adm inspect  policies.policy.mcm.ibm.com --all-namespaces 
- oc adm inspect  PlacementBinding.mcm.ibm --all-namespaces 
- oc adm inspect clusterdeployments.hive.openshift.io --all-namespaces
- oc adm inspect clusterimagesets.hive.openshift.io --all-namespaces
- oc adm inspect machinesets.machine.openshift.io --all-namespaces 
- oc adm inspect  spokeviews.view.open-cluster-management.io --all-namespaces
- oc adm inspect  clusteractions.action.open-cluster-management.io --all-namespaces
- oc adm inspect  manifestworks.work.open-cluster-management.io --all-namespaces
- oc adm inspect  spokeclusters.cluster.open-cluster-management.io --all-namespaces
- oc adm inspect  clusterinfos.internal.open-cluster-management.io --all-namespaces
- oc adm inspect  hubcores.nucleus.open-cluster-management.io --all-namespaces
- oc adm inspect  spokecores.nucleus.open-cluster-management.io --all-namespaces

### If run on Managed Cluster, it collects (is being updated soon to match New APIs):
- oc adm inspect ns/multicluster-endpoint
- oc adm inspect endpoints.multicloud.ibm.com --all-namespaces  
- oc adm inspect workmanagers.multicloud.ibm.com --all-namespaces 


