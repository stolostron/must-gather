# must-gather script for ACM

This is experimental right now. 

## Usage

```sh
oc adm must-gather --image=quay.io/open-cluster-management/must-gather
```

Note - we will have to run it differently during development. During development, we will get permission errors if we try to run for example:

```sh
oc adm must-gather --image=quay.io/open-cluster-management/must-gather:0.1.0-be85c307b7dabbadc0c1571345913a720f40e288
```
## Following commands will be run under the covers:

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

To Do:
1. We do need to be able to dynamically figure out the namespace in which ACM is installed instead of hard coded ns/open-cluster-management.
2. We need to see if we can get troubled Managed Cluster (aka Spoke Cluster) data using this script or perhaps give suggestions on which Managed Clusters this needs to be run.
3. We need to dynamically change what we run depending on this is being run on ACM-Hub or Managed Cluster.
