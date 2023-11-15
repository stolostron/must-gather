from prometheus_api_client import *
#import prometheus_api_client
import datetime
import sys
import numpy as np
import pandas
import utility
from colorama import Fore, Back, Style
import matplotlib.pyplot as plt

def checkACMContainerStatus(startTime, endTime, step):
    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print("ACM Pod/Container Health Check")
    pc=utility.promConnect()
    print("************************************************************************************************")
    print(Style.RESET_ALL)
    status = True

    status=managedClusterCount(pc,startTime, endTime, step)
    status=managedClusterReportingCount(pc,startTime, endTime, step)
    status=acmObsTimeSeriesCount(pc,startTime, endTime, step)
    status=restartCount(pc,startTime, endTime, step)
    status=checkPV(pc,startTime, endTime, step)
    status=checkContainerCount(pc,startTime, endTime, step)
    status=majorAlertCount(pc,startTime, endTime, step)


    
    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print(" ACM Pod/Container Health Check  - ", "PLEASE CHECK to see if the results are concerning!! ")
    print("************************************************************************************************")
    print(Style.RESET_ALL)
    return status

def managedClusterCount(pc,startTime, endTime, step):

    print("Number of managed clusters")
    
    try:
        mc_count_data = pc.custom_query('max(apiserver_storage_objects{resource=~"managedclusters.cluster.open-cluster-management.io"})')
        #mc_count_data = pc.custom_query('count(acm_managed_cluster_labels{})')    
        mc_count_data_df = MetricSnapshotDataFrame(mc_count_data)
        mc_count_data_df["value"]=mc_count_data_df["value"].astype(int)
        mc_count_data_df.rename(columns={"value": "ManagedClusterCount"}, inplace = True)
        print(mc_count_data_df[['ManagedClusterCount']].to_markdown())

        managed_cluster_add = pc.custom_query_range(
        query='max(apiserver_storage_objects{resource=~"managedclusters.cluster.open-cluster-management.io"})',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        managed_cluster_add_df = MetricRangeDataFrame(managed_cluster_add)
        managed_cluster_add_df["value"]=managed_cluster_add_df["value"].astype(float)
        managed_cluster_add_df.index= pandas.to_datetime(managed_cluster_add_df.index, unit="s")
        managed_cluster_add_df.rename(columns = {'value':'ManagedClusterCount'}, inplace = True)
        managed_cluster_add_df.plot(title="Number of Managed clusters connected to Hub",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/managed-cluster-count.png')
        utility.setInitialDF(managed_cluster_add_df)
        utility.saveCSV( managed_cluster_add_df, "managed-cluster-count",True)
        #utility.setInitialDF(managed_cluster_add_df)
        plt.close('all')
    except Exception as e:
        print(Fore.RED+"Error in getting the number of managed clusters: ", e)
        print(Style.RESET_ALL)
    print("=============================================")
    
    status=True
    return status 

def acmObsTimeSeriesCount(pc,startTime, endTime, step):

    print("Number of TimeSeries being sent to ACM Observability")
    
    try:
        mc_count_data = pc.custom_query('sum(acm_prometheus_tsdb_head_series)/3')   
        mc_count_data_df = MetricSnapshotDataFrame(mc_count_data)
        mc_count_data_df["value"]=mc_count_data_df["value"].astype(int)
        mc_count_data_df.rename(columns={"value": "TimeSeriesCount"}, inplace = True)
        print(mc_count_data_df[['TimeSeriesCount']].to_markdown())

        managed_cluster_add = pc.custom_query_range(
        query='sum(acm_prometheus_tsdb_head_series)/3',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        managed_cluster_add_df = MetricRangeDataFrame(managed_cluster_add)
        managed_cluster_add_df["value"]=managed_cluster_add_df["value"].astype(float)
        managed_cluster_add_df.index= pandas.to_datetime(managed_cluster_add_df.index, unit="s")
        managed_cluster_add_df.rename(columns={"value": "TimeSeriesCount"}, inplace = True)
        managed_cluster_add_df.plot(title="Number of TimeSeries being sent to ACM Observability",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/obs-timeseries-count.png')
        utility.saveCSV( managed_cluster_add_df, "obs-timeseries-count",True)
        plt.close('all')
    except Exception as e:
        print(Fore.RED+"Error in getting the number of timeseries send to ACM Obs - ACM Obs may not be configured: ", e)
        print(Style.RESET_ALL)
    print("=============================================")
    
    status=True
    return status 

def restartCount(pc,startTime, endTime, step):

    print("Checking if ACM pods are restarting frequently")

    try:
        restart_data = pc.custom_query('sum(kube_pod_container_status_restarts_total{namespace=~"multicluster-engine|open-cluster-managemen.+"}) by (namespace,container)')
        restart_data_df = MetricSnapshotDataFrame(restart_data)
        restart_data_df["value"]=restart_data_df["value"].astype(int)
        restart_data_df.rename(columns={"value": "RestartCount"}, inplace = True)
        print(restart_data_df[['container','namespace','RestartCount']].to_markdown())

        restart_data_trend = pc.custom_query_range(
        query='sum(kube_pod_container_status_restarts_total{namespace=~"multicluster-engine|open-cluster-managemen.+"}) by (namespace)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        restart_data_trend_df = MetricRangeDataFrame(restart_data_trend)
        restart_data_trend_df["value"]=restart_data_trend_df["value"].astype(float)
        restart_data_trend_df.index= pandas.to_datetime(restart_data_trend_df.index, unit="s")
        restart_data_trend_df =  restart_data_trend_df.pivot( columns='namespace',values='value')
        restart_data_trend_df.rename(columns={"value": "TimeSeriesCount"}, inplace = True)
        restart_data_trend_df.plot(title="Number of container restarts in ACM pods",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/breakdown/container-restart-count.png')    
        utility.saveCSV( restart_data_trend_df, "container-restart-count")
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"No ACM pods are restarting frequently - all GOOD!!: ",e)
        print(Style.RESET_ALL)    
    print("==============================================")

    status=True
    return status    

def checkPV(pc,startTime, endTime, step):
    try:
        print("Checking amount of percent free space left in PVs needed by ACM")
        
        pv_data = pc.custom_query('sum by (persistentvolumeclaim) ((kubelet_volume_stats_available_bytes{namespace="open-cluster-management-observability"})*100/(kubelet_volume_stats_capacity_bytes{namespace="open-cluster-management-observability"}))')
        pv_data_df = MetricSnapshotDataFrame(pv_data)
        pv_data_df["value"]=pv_data_df["value"].astype(float)
        pv_data_df.rename(columns={"value": "FreeSpaceAvailPct"}, inplace = True)
        print(pv_data_df[['persistentvolumeclaim','FreeSpaceAvailPct']].to_markdown())

        pv_data_trend = pc.custom_query_range(
        query='sum by (persistentvolumeclaim) ((kubelet_volume_stats_available_bytes{namespace="open-cluster-management-observability"})*100/(kubelet_volume_stats_capacity_bytes{namespace="open-cluster-management-observability"}))',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        pv_data_trend_df = MetricRangeDataFrame(pv_data_trend)
        pv_data_trend_df["value"]=pv_data_trend_df["value"].astype(float)
        pv_data_trend_df.index= pandas.to_datetime(pv_data_trend_df.index, unit="s")
        pv_data_trend_df =  pv_data_trend_df.pivot( columns='persistentvolumeclaim',values='value')
        pv_data_trend_df.rename(columns={"value": "TimeSeriesCount"}, inplace = True)
        pv_data_trend_df.plot(title="Amount of percent free space left in PVs needed by ACM",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/breakdown/acm-pv-free-space.png')
        utility.saveCSV( pv_data_trend_df, "acm-pv-free-space")
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error - Checking amount of percent free space left in PVs needed by ACM: ",e) 
        print(Style.RESET_ALL) 
        #pass   
    print("==============================================")
    
    status=True
    return status   

def checkContainerCount(pc,startTime, endTime, step):
    
    #start_time, end_time,step = helperTime()

    print("Checking number of Pods running in the ACM namespaces")

    try:
        container_data = pc.custom_query('sum by (namespace) (kube_pod_info{namespace=~"open-cluster-managemen.+"})')
        container_data_df = MetricSnapshotDataFrame(container_data)
        container_data_df["value"]=container_data_df["value"].astype(int)
        container_data_df.rename(columns={"value": "PodCount"}, inplace = True)
        print(container_data_df[['namespace','PodCount']].to_markdown())

        container_data_trend = pc.custom_query_range(
        query='sum by (namespace) (kube_pod_info{namespace=~"open-cluster-managemen.+"})',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        container_data_trend_df = MetricRangeDataFrame(container_data_trend)
        container_data_trend_df["value"]=container_data_trend_df["value"].astype(float)
        container_data_trend_df.index= pandas.to_datetime(container_data_trend_df.index, unit="s")
        container_data_trend_df =  container_data_trend_df.pivot( columns='namespace',values='value')
        container_data_trend_df.rename(columns={"value": "PodCount"}, inplace = True)
        container_data_trend_df.plot(title="Number of Pods running in the ACM namespaces",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/breakdown/running-pod-count-acm.png')
        utility.saveCSV( container_data_trend_df, "running-pod-count-acm")
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error - Checking number of Pods running in the ACM namespaces: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
    
    status=True
    return status  

def majorAlertCount(pc,startTime, endTime, step):

    try:
        print("Checking all alerts currently firing under Hub Cluster that have triggered more than once")
        alert_data = pc.custom_query('sum by (alertname) (ALERTS{alertstate="firing"}) >1')

        alert_data_df = MetricSnapshotDataFrame(alert_data)
        alert_data_df["value"]=alert_data_df["value"].astype(int)
        print(alert_data_df[['alertname','value']].to_markdown())

        alert_data_trend = pc.custom_query_range(
        query='sum by (alertname) (ALERTS{alertstate="firing"}) >1',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        alert_data_trend_df = MetricRangeDataFrame(alert_data_trend)
        alert_data_trend_df["value"]=alert_data_trend_df["value"].astype(float)
        alert_data_trend_df.index= pandas.to_datetime(alert_data_trend_df.index, unit="s")
        alert_data_trend_df =  alert_data_trend_df.pivot( columns='alertname',values='value')
        alert_data_trend_df.rename(columns={"value": "AlertCount"}, inplace = True)
        alert_data_trend_df.plot(title="Alerts currently firing under Hub Cluster",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/breakdown/firing-alert-count.png')
        utility.saveCSV( alert_data_trend_df, "firing-alert-count")
        plt.close('all')
    except Exception as e:
        print(Fore.RED+"Error in getting all alerts currently firing under Hub Cluster that have triggered more than once: ",e)
        print(Style.RESET_ALL)
        #pass   
    print("=============================================")
    
    status=True
    return status   

def managedClusterReportingCount(pc,startTime, endTime, step):

    print("Number of managed clusters reporting")
    
    try:
        mc_count_data = pc.custom_query('sum(acm_managed_cluster_info{available="True"})')
        #mc_count_data = pc.custom_query('count(acm_managed_cluster_labels{})')    
        mc_count_data_df = MetricSnapshotDataFrame(mc_count_data)
        mc_count_data_df["value"]=mc_count_data_df["value"].astype(int)
        mc_count_data_df.rename(columns={"value": "ManagedClusterReportCount"}, inplace = True)
        print(mc_count_data_df[['ManagedClusterReportCount']].to_markdown())

        managed_cluster_add = pc.custom_query_range(
        query='sum(acm_managed_cluster_info{available="True"})',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        managed_cluster_add_df = MetricRangeDataFrame(managed_cluster_add)
        managed_cluster_add_df["value"]=managed_cluster_add_df["value"].astype(float)
        managed_cluster_add_df.index= pandas.to_datetime(managed_cluster_add_df.index, unit="s")
        managed_cluster_add_df.rename(columns = {'value':'ManagedClusterReportCount'}, inplace = True)
        managed_cluster_add_df.plot(title="Number of Managed clusters connected and Reporting to Hub",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/managed-report-cluster-count.png')
        utility.setInitialDF(managed_cluster_add_df)
        utility.saveCSV( managed_cluster_add_df, "managed-cluster-report-count",True)
        #utility.setInitialDF(managed_cluster_add_df)
        plt.close('all')
    except Exception as e:
        print(Fore.RED+"Error in getting the number of managed clusters reporting: ", e)
        print(Style.RESET_ALL)
    print("=============================================")
    
    status=True
    return status 
