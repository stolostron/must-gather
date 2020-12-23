# must-gather script for ACM

This is experimental as of now.   

## Usage

```sh
oc adm must-gather --image=quay.io/open-cluster-management/must-gather:0.1.0-SNAPSHOT-2020-06-....
```

If you need the results to be saved in a named directory, then following the must-gather instructions, this can be run. Also added are commands to create a gzipped tarball:

```sh
oc adm must-gather --image=quay.io/open-cluster-management/must-gather:0.1.0-SNAPSHOT-2020-06-.... --dest-dir=SOMENAME ; tar -cvzf SOMENAME.tgz SOMENAME
```

In addition, if we need to collect must-gather for the OpenShift infrastructure, we can run:
```
oc adm must-gather
```

## Information Captured
1. The above must-gather command can understand where it is being run - ACM Hub Server or Managed Cluster and collects data accordingly.
2. If run on the ACM Hub Server, it will also capture a list of Managed Clusters configured and the status. This is found in the `gather-managed.log` If a Managed Cluster reports a status of not equal to Ready when it is expected to be, then the must-gather command above should be run on the Managed Cluster as well.

### Data collected

![Must Gather Layout](images/must-gather-image.png)


Let us go through what is collected:
1. The data is organized under 2 levels - cluster scoped resources and the resources that belong to namespaces (that we have decided to collect)
2. The data is further organized by API group for the custom resource definitions. This is true for both cluster scope and namespace scoped resources.
3. And we can see the Kind for the custom resource defintions.
4. At the leaf level, we can see the `yaml for each of the custom resources for the kind`
5. This log contains the output of `kubectl get pods -n $NAMESPACE-IN-WHICH-ACM-RUNS-ON-HUB`.
6. If run on the ACM Hub Server, the list of Managed Clusters configured and their status is captured in this log.
7. The list of namespace for each the data is collected. And the output of one namespace is expanded. The other namespaces when expanded will look the same. 
8. This is the list of Pods running in each namespace. If a namespace does not contain any pods, this will be not be there.

Data collected for the PODs include:
![POD Data collected](images/pod-data.png)

If we take a look at the cluster-manager POD for example you will see the yaml file which contains detailed output of the POD. You can see the container called registration-operator and its logs.

### If run on ACM Hub, it collects (is being updated soon to match New APIs):

#### Following Namespaces
- namspace in which OCM is running (dynamically discovered)
- hive

#### Following CRD
- multiclusterhubs.operators.open-cluster-management.io
- endpointconfigs.multicloud.ibm.com
- hiveconfigs.hive.openshift.io
- clusterdeployments.hive.openshift.io
- clusterimagesets.hive.openshift.io
- machinesets.machine.openshift.io 
- applications.app.k8s.io
- channels.apps.open-cluster-management.io
- deployables.apps.open-cluster-management.io
- placementrules.apps.open-cluster-management.io
- subscriptions.apps.open-cluster-management.io
- policies.policy.mcm.ibm.com
- PlacementBinding.mcm.ibm 
- spokeviews.view.open-cluster-management.io
- clusteractions.action.open-cluster-management.io
- manifestworks.work.open-cluster-management.io
- spokeclusters.cluster.open-cluster-management.io
- clusterinfos.internal.open-cluster-management.io
- hubcores.nucleus.open-cluster-management.io
- spokecores.nucleus.open-cluster-management.io
- discoveredclusterrefreshes.discovery.open-cluster-management.io
- discoveredclusters.discovery.open-cluster-management.io
- discoveryconfigs.discovery.open-cluster-management.io
- searchoperators.search.open-cluster-management.io
- searchcustomizations.search.open-cluster-management.io

### If run on Managed Cluster, it collects (is being updated soon to match New APIs):

#### Following Namespaces
- multicluster-endpoint

#### Following CRDs
- endpoints.multicloud.ibm.com
- workmanagers.multicloud.ibm.com


