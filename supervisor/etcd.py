from prometheus_api_client import *
#import prometheus_api_client
import datetime
import sys
import numpy as np
import pandas
import utility
from colorama import Fore, Back, Style
import matplotlib.pyplot as plt

def checkEtcdStatus(startTime, endTime, step):
    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print("Etcd Health Check")
    pc=utility.promConnect()
    print("************************************************************************************************")
    print(Style.RESET_ALL)
    status = True

    #pc=utility.promConnect()

    status=etcdDBSize(pc,startTime, endTime, step)
    status=etcdDBSizeInUse(pc,startTime, endTime, step)
    status=etcdLeaderChanges(pc,startTime, endTime, step)
    status=etcdBackendCommitDuration(pc,startTime, endTime, step)
    status=etcdDiskWalsyncDuration(pc,startTime, endTime, step)
    status=etcdNetworkPeerRounTripDuration(pc,startTime, endTime, step)
    status=etcdCPUIowaitDuration(pc,startTime, endTime, step)


    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print("Etcd Health Check  - ", "PLEASE CHECK to see if the results are concerning!! ")
    print("************************************************************************************************")
    print(Style.RESET_ALL)
    return status
 

def etcdDBSize(pc,startTime, endTime, step):

    print("Checking etcd Size in MB")

    try:
        etcd_data = pc.custom_query('etcd_mvcc_db_total_size_in_bytes{job="etcd"}/(1024*1024)')

        etcd_data_df = MetricSnapshotDataFrame(etcd_data)
        etcd_data_df["value"]=etcd_data_df["value"].astype(float)
        etcd_data_df.rename(columns={"value": "etcdDBSizeMB"}, inplace = True)
        print(etcd_data_df[['instance','etcdDBSizeMB']].to_markdown())

        etcd_data_trend = pc.custom_query_range(
        query='etcd_mvcc_db_total_size_in_bytes{job="etcd"}/(1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        etcd_data_trend_df = MetricRangeDataFrame(etcd_data_trend)
        etcd_data_trend_df["value"]=etcd_data_trend_df["value"].astype(float)
        etcd_data_trend_df.index= pandas.to_datetime(etcd_data_trend_df.index, unit="s")
        etcd_data_trend_df =  etcd_data_trend_df.pivot( columns='instance',values='value')
        etcd_data_trend_df.plot(title="Etcd DB size Details in MB",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/breakdown/etcd-size-detail.png')
        utility.saveCSV(etcd_data_trend_df,'etcd-size-detail')
        plt.close('all')

        """ 
        ax=df.plot(title="Node (Worker) CPU Utilisation Percent Rate")
        ax.legend(bbox_to_anchor=(0., 1.06, 1., .102), loc='lower left', ncol=2, mode="expand", borderaxespad=0.)
        #plt.legend(loc='lower left',ncol=3)
        #plt.show()
        #print(df.head(5))
        """
        # calculating the sum of all the etcd db size - w/o instance details
        etcd_data_sum_trend = pc.custom_query_range(
        query='sum(etcd_mvcc_db_total_size_in_bytes{job="etcd"})/(1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        etcd_data_sum_trend_df = MetricRangeDataFrame(etcd_data_sum_trend)
        etcd_data_sum_trend_df["value"]=etcd_data_sum_trend_df["value"].astype(float)
        etcd_data_sum_trend_df.index= pandas.to_datetime(etcd_data_sum_trend_df.index, unit="s")
        etcd_data_sum_trend_df.rename(columns={"value": "etcdDBSizeMB"}, inplace = True)
        #etcd_data_sum_trend_df =  etcd_data_sum_trend_df.pivot( columns='instance',values='value')
        etcd_data_sum_trend_df.plot(title="Etcd DB size in MB",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/etcd-size.png')
        utility.saveCSV(etcd_data_sum_trend_df,'etcd-size',True) 
        plt.close('all')   
    except Exception as e:
        print(Fore.RED+"Error in getting etcd db size in MB: ",e)    
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status       

def etcdDBSizeInUse(pc,startTime, endTime, step):

    print("Checking etcd Space In Used in MB")

    try:
        etcd_use_data = pc.custom_query('etcd_mvcc_db_total_size_in_use_in_bytes{job="etcd"}/(1024*1024)')

        etcd_use_data_df = MetricSnapshotDataFrame(etcd_use_data)
        etcd_use_data_df["value"]=etcd_use_data_df["value"].astype(float)
        etcd_use_data_df.rename(columns={"value": "etcdDBSizeInUseMB"}, inplace = True)
        print(etcd_use_data_df[['instance','etcdDBSizeInUseMB']].to_markdown())

        etcd_data_trend = pc.custom_query_range(
        query='etcd_mvcc_db_total_size_in_use_in_bytes{job="etcd"}/(1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        etcd_data_trend_df = MetricRangeDataFrame(etcd_data_trend)
        etcd_data_trend_df["value"]=etcd_data_trend_df["value"].astype(float)
        etcd_data_trend_df.index= pandas.to_datetime(etcd_data_trend_df.index, unit="s")
        etcd_data_trend_df =  etcd_data_trend_df.pivot( columns='instance',values='value')
        etcd_data_trend_df.plot(title="Etcd space consumed Details in MB",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/breakdown/etcd-space-consumed-detail.png')
        utility.saveCSV(etcd_data_trend_df,'etcd-space-consumed-detail')
        plt.close('all')

        # calculating the sum of all the etcd db size - w/o instance details
        etcd_data_sum_trend = pc.custom_query_range(
        query='sum(etcd_mvcc_db_total_size_in_use_in_bytes{job="etcd"})/(1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        etcd_data_sum_trend_df = MetricRangeDataFrame(etcd_data_sum_trend)
        etcd_data_sum_trend_df["value"]=etcd_data_sum_trend_df["value"].astype(float)
        etcd_data_sum_trend_df.index= pandas.to_datetime(etcd_data_sum_trend_df.index, unit="s")
        etcd_data_sum_trend_df.rename(columns={"value": "etcdDBSizeUsedMB"}, inplace = True)
        etcd_data_sum_trend_df.plot(title="Etcd space consumed in MB",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/etcd-space-consumed.png')
        utility.saveCSV(etcd_data_sum_trend_df,'etcd-space-consumed',True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting etcd space in use in MB: ",e)
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status       

def etcdLeaderChanges(pc,startTime, endTime, step):

    print("Checking leader election counts in etcd")
    
    try:
        etcd_leader_data = pc.custom_query('changes(etcd_server_leader_changes_seen_total{job="etcd"}[1d])')
        #print(etcd_leader_data)
        etcd_leader_data_df = MetricSnapshotDataFrame(etcd_leader_data)
        etcd_leader_data_df["value"]=etcd_leader_data_df["value"].astype(int)
        etcd_leader_data_df.rename(columns={"value": "LeaderChanges"}, inplace = True)
        print(etcd_leader_data_df[['instance','LeaderChanges']].to_markdown())
    
        etcd_data_trend = pc.custom_query_range(
        query='changes(etcd_server_leader_changes_seen_total{job="etcd"}[1d])',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        etcd_data_trend_df = MetricRangeDataFrame(etcd_data_trend)
        etcd_data_trend_df["value"]=etcd_data_trend_df["value"].astype(float)
        etcd_data_trend_df.index= pandas.to_datetime(etcd_data_trend_df.index, unit="s")
        etcd_data_trend_df =  etcd_data_trend_df.pivot( columns='instance',values='value')
        etcd_data_trend_df.plot(title="Etcd leader election counts Details",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/breakdown/etcd-leader-election-count-detal.png')
        utility.saveCSV(etcd_data_trend_df,'etcd-leader-election-count-detail')
        plt.close('all')

        # calculating the sum of all the leader changes - w/o instance details
        etcd_data_sum_trend = pc.custom_query_range(
        query='sum(changes(etcd_server_leader_changes_seen_total{job="etcd"}[1d]))',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        etcd_data_sum_trend_df = MetricRangeDataFrame(etcd_data_sum_trend)
        etcd_data_sum_trend_df["value"]=etcd_data_sum_trend_df["value"].astype(float)
        etcd_data_sum_trend_df.index= pandas.to_datetime(etcd_data_sum_trend_df.index, unit="s")
        etcd_data_sum_trend_df.rename(columns={"value": "etcdDBLeaderElection"}, inplace = True)
        etcd_data_sum_trend_df.plot(title="Etcd leader election counts",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/etcd-leader-election-count.png')
        utility.saveCSV(etcd_data_sum_trend_df,'etcd-leader-election-count',True) 
        plt.close('all')    
    except Exception as e:
        print(Fore.RED+"Error in getting leader election counts in etcd: ",e)
        print(Style.RESET_ALL)

    print("=============================================")
    
    status=True
    return status   

def etcdBackendCommitDuration(pc,startTime, endTime, step):

    print("Checking etcd backend commit duration 99th Percentile in seconds")

    try:
        etcd_data = pc.custom_query('histogram_quantile(0.99, irate(etcd_disk_backend_commit_duration_seconds_bucket[5m]))')

        etcd_data_df = MetricSnapshotDataFrame(etcd_data)
        etcd_data_df["value"]=etcd_data_df["value"].astype(float)
        etcd_data_df.rename(columns={"value": "etcdBackendCommitDuration"}, inplace = True)
        print(etcd_data_df[['instance','etcdBackendCommitDuration']].to_markdown())

        etcd_data_trend = pc.custom_query_range(
        query='histogram_quantile(0.99, irate(etcd_disk_backend_commit_duration_seconds_bucket[5m]))',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        etcd_data_trend_df = MetricRangeDataFrame(etcd_data_trend)
        etcd_data_trend_df["value"]=etcd_data_trend_df["value"].astype(float)
        etcd_data_trend_df.index= pandas.to_datetime(etcd_data_trend_df.index, unit="s")
        etcd_data_trend_df =  etcd_data_trend_df.pivot( columns='instance',values='value')
        etcd_data_trend_df.plot(title="Etcd Backend Commit Duration 99th Percentile in seconds",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/breakdown/etcd-backend-commit-duration-detail.png')
        utility.saveCSV(etcd_data_trend_df,'etcd-backend-commit-duration-detail')
        plt.close('all')

        # calculating the max  - w/o instance details
        etcd_data_sum_trend = pc.custom_query_range(
        query='max(histogram_quantile(0.99, irate(etcd_disk_backend_commit_duration_seconds_bucket[5m])))',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        etcd_data_sum_trend_df = MetricRangeDataFrame(etcd_data_sum_trend)
        etcd_data_sum_trend_df["value"]=etcd_data_sum_trend_df["value"].astype(float)
        etcd_data_sum_trend_df.index= pandas.to_datetime(etcd_data_sum_trend_df.index, unit="s")
        etcd_data_sum_trend_df.rename(columns={"value": "etcdBackendCommitDuration"}, inplace = True)
        etcd_data_sum_trend_df.plot(title="Etcd Backend Commit Duration 99th Percentile in seconds",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/etcd-backend-commit-duration.png')
        utility.saveCSV(etcd_data_sum_trend_df,'etcd-backend-commit-duration',True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting etcd backend commit duration: ",e)
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status       

def etcdDiskWalsyncDuration(pc,startTime, endTime, step):

    print("Checking etcd Wal Sync duration 99th Percentile in seconds")

    try:
        etcd_data = pc.custom_query('histogram_quantile(0.99, irate(etcd_disk_wal_fsync_duration_seconds_bucket[5m]))')

        etcd_data_df = MetricSnapshotDataFrame(etcd_data)
        etcd_data_df["value"]=etcd_data_df["value"].astype(float)
        etcd_data_df.rename(columns={"value": "etcdWalSyncDuration"}, inplace = True)
        print(etcd_data_df[['instance','etcdWalSyncDuration']].to_markdown())

        etcd_data_trend = pc.custom_query_range(
        query='histogram_quantile(0.99, irate(etcd_disk_wal_fsync_duration_seconds_bucket[5m]))',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        etcd_data_trend_df = MetricRangeDataFrame(etcd_data_trend)
        etcd_data_trend_df["value"]=etcd_data_trend_df["value"].astype(float)
        etcd_data_trend_df.index= pandas.to_datetime(etcd_data_trend_df.index, unit="s")
        etcd_data_trend_df =  etcd_data_trend_df.pivot( columns='instance',values='value')
        etcd_data_trend_df.plot(title="Etcd Backend Commit Duration 99th Percentile in seconds",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/breakdown/etcd-wal-sync-duration-detail.png')
        utility.saveCSV(etcd_data_trend_df,'etcd-wal-sync-duration-detail')
        plt.close('all')

        # calculating the max  - w/o instance details
        etcd_data_sum_trend = pc.custom_query_range(
        query='max(histogram_quantile(0.99, irate(etcd_disk_wal_fsync_duration_seconds_bucket[5m])))',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        etcd_data_sum_trend_df = MetricRangeDataFrame(etcd_data_sum_trend)
        etcd_data_sum_trend_df["value"]=etcd_data_sum_trend_df["value"].astype(float)
        etcd_data_sum_trend_df.index= pandas.to_datetime(etcd_data_sum_trend_df.index, unit="s")
        etcd_data_sum_trend_df.rename(columns={"value": "etcdWalSyncDuration"}, inplace = True)
        etcd_data_sum_trend_df.plot(title="Etcd Wal Sync Duration 99th Percentile in seconds",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/etcd-wal-sync-duration.png')
        utility.saveCSV(etcd_data_sum_trend_df,'etcd-wal-sync-duration',True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting etcd backend commit duration: ",e)
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status       

def etcdNetworkPeerRounTripDuration(pc,startTime, endTime, step):

    print("Checking etcd network peer roundtrip duration 99th Percentile in seconds")

    try:
        etcd_data = pc.custom_query('histogram_quantile(0.99, irate(etcd_network_peer_round_trip_time_seconds_bucket[5m]))')

        etcd_data_df = MetricSnapshotDataFrame(etcd_data)
        etcd_data_df["value"]=etcd_data_df["value"].astype(float)
        etcd_data_df.rename(columns={"value": "etcdNetWorkPeerRoundTripDuration"}, inplace = True)
        # instance by itself is not unique anymore because these is between instances
        # and therefore as 2 values. Example a->b and b->a
        print(etcd_data_df[['instance','To','etcdNetWorkPeerRoundTripDuration']].to_markdown())

        etcd_data_trend = pc.custom_query_range(
        query='histogram_quantile(0.99, irate(etcd_network_peer_round_trip_time_seconds_bucket[5m]))',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        etcd_data_trend_df = MetricRangeDataFrame(etcd_data_trend)
        etcd_data_trend_df["value"]=etcd_data_trend_df["value"].astype(float)
        etcd_data_trend_df.index= pandas.to_datetime(etcd_data_trend_df.index, unit="s")
        etcd_data_trend_df =  etcd_data_trend_df.pivot( columns=['instance','To'],values='value')
        etcd_data_trend_df.plot(title="Etcd Network Peer RoundTrip Duration 99th Percentile in seconds",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/breakdown/etcd-network-peer-roundtrip-duration-detail.png')
        utility.saveCSV(etcd_data_trend_df,'etcd-network-peer-roundtrip-duration-detail')
        plt.close('all')

        # calculating the max  - w/o instance details
        etcd_data_sum_trend = pc.custom_query_range(
        query='max(histogram_quantile(0.99, irate(etcd_network_peer_round_trip_time_seconds_bucket[5m])))',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        etcd_data_sum_trend_df = MetricRangeDataFrame(etcd_data_sum_trend)
        etcd_data_sum_trend_df["value"]=etcd_data_sum_trend_df["value"].astype(float)
        etcd_data_sum_trend_df.index= pandas.to_datetime(etcd_data_sum_trend_df.index, unit="s")
        etcd_data_sum_trend_df.rename(columns={"value": "etcdNetWorkPeerRoundTripDuration"}, inplace = True)
        etcd_data_sum_trend_df.plot(title="Etcd Network Peer RoundTrip Duration 99th Percentile in seconds",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/etcd-network-peer-roundtrip-duration.png')
        utility.saveCSV(etcd_data_sum_trend_df,'etcd-network-peer-roundtrip-duration',True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting etcd network peer roundtrip duration: ",e)
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status       

def etcdCPUIowaitDuration(pc,startTime, endTime, step):

    print("Checking etcd CU IOWait Duration in seconds")
    try:
        etcd_data = pc.custom_query('(sum(irate(node_cpu_seconds_total {mode="iowait"} [2m])) without (cpu)) / count(node_cpu_seconds_total) without (cpu) * 100 AND on (instance) label_replace( kube_node_role{role="master"}, "instance", "$1", "node", "(.+)" )')

        etcd_data_df = MetricSnapshotDataFrame(etcd_data)
        etcd_data_df["value"]=etcd_data_df["value"].astype(float)
        etcd_data_df.rename(columns={"value": "etcdCPUIOWaitDuration"}, inplace = True)
        print(etcd_data_df[['instance','etcdCPUIOWaitDuration']].to_markdown())

        etcd_data_trend = pc.custom_query_range(
        query='(sum(irate(node_cpu_seconds_total {mode="iowait"} [2m])) without (cpu)) / count(node_cpu_seconds_total) without (cpu) * 100 AND on (instance) label_replace( kube_node_role{role="master"}, "instance", "$1", "node", "(.+)" )',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        etcd_data_trend_df = MetricRangeDataFrame(etcd_data_trend)
        etcd_data_trend_df["value"]=etcd_data_trend_df["value"].astype(float)
        etcd_data_trend_df.index= pandas.to_datetime(etcd_data_trend_df.index, unit="s")
        etcd_data_trend_df =  etcd_data_trend_df.pivot( columns='instance',values='value')
        etcd_data_trend_df.plot(title="Etcd CPU IOWait Duration in seconds",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/breakdown/etcd-cpu-iowait-duration-detail.png')
        utility.saveCSV(etcd_data_trend_df,'etcd-cpu-iowait-duration-detail')
        plt.close('all')

        # calculating the max  - w/o instance details
        etcd_data_sum_trend = pc.custom_query_range(
        query='max((sum(irate(node_cpu_seconds_total {mode="iowait"} [2m])) without (cpu)) / count(node_cpu_seconds_total) without (cpu) * 100 AND on (instance) label_replace( kube_node_role{role="master"}, "instance", "$1", "node", "(.+)" ))',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        etcd_data_sum_trend_df = MetricRangeDataFrame(etcd_data_sum_trend)
        etcd_data_sum_trend_df["value"]=etcd_data_sum_trend_df["value"].astype(float)
        etcd_data_sum_trend_df.index= pandas.to_datetime(etcd_data_sum_trend_df.index, unit="s")
        etcd_data_sum_trend_df.rename(columns={"value": "etcdCPUIOWaitDuration"}, inplace = True)
        etcd_data_sum_trend_df.plot(title="Etcd CPU IOWait Duration in seconds",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/etcd-cpu-iowait-duration.png')
        utility.saveCSV(etcd_data_sum_trend_df,'etcd-cpu-iowait-duration',True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting etcd CPU IOWait duration: ",e)
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status       