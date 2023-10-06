from prometheus_api_client import *
#import prometheus_api_client
import datetime
import sys
import numpy as np
import pandas
from utility import *

def checkACMHubClusterUtilization():
    print("ACM Pod/Container Health Check")
    status = True

    pc=promConnect()
    status=managedClusterCount(pc)
    status=etcdDBSize(pc)
    status=etcdDBSizeInUse(pc)
    status=etcdLeaderChanges(pc)

    #status=apiServerLatency(pc)

    status=restartCount(pc)
    
    #status=checkPV(pc)
    #status=checkContainerCount(pc)
   
    #status=majorAlertCount(pc)
    
    

    print(" ============ Hub Cluster Sizing Parameters -**!! =======")
    return status

def managedClusterCount(pc):

    print("Number of managed clusters")
    #mc_count_data = pc.custom_query('max(apiserver_storage_objects{resource=~"managedclusters.cluster.open-cluster-management.io"})')
    mc_count_data = pc.custom_query('count(acm_managed_cluster_labels{})')
    
    mc_count_data_df = MetricSnapshotDataFrame(mc_count_data);
    mc_count_data_df["value"]=mc_count_data_df["value"].astype(int)
    mc_count_data_df.rename(columns={"value": "ManagedClusterCount"}, inplace = True)
    print(mc_count_data_df[['ManagedClusterCount']])
    
    print("=============================================")
    
    status=True
    return status 

def etcdDBSize(pc):

    print("Checking etcd Space consumption in MB")
    etcd_data = pc.custom_query('etcd_debugging_mvcc_db_total_size_in_bytes{job="etcd",cluster="local-cluster"}/(1024*1024)')

    etcd_data_df = MetricSnapshotDataFrame(etcd_data);
    etcd_data_df["value"]=etcd_data_df["value"].astype(float)
    etcd_data_df.rename(columns={"value": "etcdDBSizeMB"}, inplace = True)
    print(etcd_data_df[['instance','etcdDBSizeMB']])
    #print(etcd_data_df)
    print("=============================================")
   
    status=True
    return status       


def etcdDBSizeInUse(pc):

    print("Checking etcd Space In Used in MB")

    try:
        etcd_use_data = pc.custom_query('etcd_mvcc_db_total_size_in_use_in_bytes{job="etcd",cluster="local-cluster"}/(1024*1024)')

        etcd_use_data_df = MetricSnapshotDataFrame(etcd_use_data);
        etcd_use_data_df["value"]=etcd_use_data_df["value"].astype(float)
        etcd_use_data_df.rename(columns={"value": "etcdDBSizeInUseMB"}, inplace = True)
        print(etcd_use_data_df[['instance','etcdDBSizeInUseMB']])
        #print(etcd_use_data_df)
    except:
        print("Missing metric: etcd_mvcc_db_total_size_in_use_in_bytes. Check allow-list to see if it is being collected")
    print("=============================================")
   
    status=True
    return status       

def etcdLeaderChanges(pc):

    print("Checking leader election counts in etcd")
    etcd_leader_data = pc.custom_query('changes(etcd_server_leader_changes_seen_total{job="etcd",cluster="local-cluster"}[1d])')

    etcd_leader_data_df = MetricSnapshotDataFrame(etcd_leader_data);
    etcd_leader_data_df["value"]=etcd_leader_data_df["value"].astype(int)
    etcd_leader_data_df.rename(columns={"value": "LeaderChanges"}, inplace = True)
    print(etcd_leader_data_df[['instance','LeaderChanges']])
    #print(etcd_data_df)
    print("=============================================")
    
    status=True
    return status   

def apiServerLatency(pc):

    print("99th Percentile Latency of API calls to resources - Top 10")

    apiserver_latency_data = pc.custom_query('topk(10,histogram_quantile(0.99, sum(rate(apiserver_request_duration_seconds_bucket{apiserver="kube-apiserver",subresource!="log",verb!~"WATCH|WATCHLIST|PROXY"}[5m])) by(le,resource)))')
    #apiserver_latency_data = pc.custom_query('topk(10,apiserver_request_duration_seconds:histogram_quantile_99:instance
    #                                         {cluster="local-cluster",verb!~"WATCH|WATCHLIST|PROXY"}[5m])) by(le,resource)))')


    apiserver_latency_data_df = MetricSnapshotDataFrame(apiserver_latency_data);
    apiserver_latency_data_df["value"]=apiserver_latency_data_df["value"].astype(float)
    apiserver_latency_data_df.rename(columns={"value": "APIServer99PctLatency"}, inplace = True)
    print(apiserver_latency_data_df[['resource','APIServer99PctLatency']])
    print("=============================================")
    
    status=True
    return status 


def restartCount(pc):

    print("Checking if ACM pods are restarting frequently")

    try:
        restart_data = pc.custom_query('sum(kube_pod_container_status_restarts_total{namespace=~"open-cluster-managemen.+",cluster="local-cluster"}) by (namespace,container) >0')
        restart_data_df = MetricSnapshotDataFrame(restart_data);
        restart_data_df["value"]=restart_data_df["value"].astype(int)
        restart_data_df.rename(columns={"value": "RestartCount"}, inplace = True)
        print(restart_data_df[['container','namespace','RestartCount']])
    except:
        print("Missing metric: kube_pod_container_status_restarts_total. Check allow-list to see if it is being collected")

    print("==============================================")

    status=True
    return status    

def checkPV(pc):
    try:
        print("Checking amount of percent free space left in PVs needed by ACM")
        
        pv_data = pc.custom_query('sum by (persistentvolumeclaim) ((kubelet_volume_stats_available_bytes{namespace="open-cluster-management-observability"})*100/(kubelet_volume_stats_capacity_bytes{namespace="open-cluster-management-observability"}))')
        pv_data_df = MetricSnapshotDataFrame(pv_data);
        pv_data_df["value"]=pv_data_df["value"].astype(float)
        pv_data_df.rename(columns={"value": "FreeSpaceAvailPct"}, inplace = True)
        print(pv_data_df[['persistentvolumeclaim','FreeSpaceAvailPct']])
        print("==============================================")
    except Exception as e:
        #print("Failure: ",e)  
        pass   
    
    status=True
    return status   

def checkContainerCount(pc):
    
    #start_time, end_time,step = helperTime()

    print("Checking number of Pods running in the ACM namespaces")

    container_data = pc.custom_query('sum by (namespace) (kube_pod_info{namespace=~"open-cluster-managemen.+"})')

    container_data_df = MetricSnapshotDataFrame(container_data);
    container_data_df["value"]=container_data_df["value"].astype(int)
    container_data_df.rename(columns={"value": "PodCount"}, inplace = True)
    print(container_data_df[['namespace','PodCount']])
    print("=============================================")
    
    status=True
    return status  



def majorAlertCount(pc):

    try:
        print("Checking all alerts currently firing under Hub Cluster that have triggered more than once")
        alert_data = pc.custom_query('sum by (alertname) (ALERTS{alertstate="firing"}) >1')

        alert_data_df = MetricSnapshotDataFrame(alert_data);
        alert_data_df["value"]=alert_data_df["value"].astype(int)
        print(alert_data_df[['alertname','value']])
        print("=============================================")
    except Exception as e:
        #print("Failure: ",e)  
        pass   

    status=True
    return status    

  

