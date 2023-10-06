from prometheus_api_client import *
#import prometheus_api_client
import datetime
import sys
import numpy as np
import pandas
from utility import *
from colorama import Fore, Back, Style
import matplotlib.pyplot as plt

def checkThanosStatus(startTime, endTime, step):
    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print("Thanos Health Check")
    pc=promConnect()
    print("************************************************************************************************")
    print(Style.RESET_ALL)
    status = True

    #pc=promConnect()

    status=thanosCompactToDo(pc,startTime, endTime, step)
    status=thanosCompactHalt(pc,startTime, endTime, step)
    status=thanosRecvSync90(pc,startTime, endTime, step)
    status=thanosRecvSync95(pc,startTime, endTime, step)
    status=thanosRecvSync99(pc,startTime, endTime, step)
    status=thanosRecvGrpcError(pc,startTime, endTime, step)


    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print("Etcd Health Check  - ", "PLEASE CHECK to see if the results are concerning!! ")
    print("************************************************************************************************")
    print(Style.RESET_ALL)
    return status
 

def thanosCompactToDo(pc,startTime, endTime, step):

    print("Is Thanos Compact Todo Compactions Caught up?")

    try:
        compactor_data = pc.custom_query('acm_thanos_compact_todo_compactions{}')

        compactor_data_df = MetricSnapshotDataFrame(compactor_data)
        compactor_data_df["value"]=compactor_data_df["value"].astype(float)
        compactor_data_df.rename(columns={"value": "CompactorToDo"}, inplace = True)
        print(compactor_data_df[['instance','CompactorToDo']].to_markdown())

        compactor_data_trend = pc.custom_query_range(
        query='acm_thanos_compact_todo_compactions{}',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        compactor_data_trend_df = MetricRangeDataFrame(compactor_data_trend)
        compactor_data_trend_df["value"]=compactor_data_trend_df["value"].astype(float)
        compactor_data_trend_df.index= pandas.to_datetime(compactor_data_trend_df.index, unit="s")
        compactor_data_trend_df.rename(columns={"value": "CompactorToDo"}, inplace = True)
        compactor_data_trend_df.plot(title="Thanos Compactor To Do compactions",figsize=(30, 15))
        plt.savefig('../../output/thanos-compact-todo-compaction.png')
        saveCSV(compactor_data_trend_df[['CompactorToDo']],'thanos-compact-todo-compaction',True)
        plt.close('all')
  
    except Exception as e:
        print(Fore.RED+"Error in gathering thanos compactor to do compaction data (may be it is up to date): ",e)    
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status       

def thanosCompactHalt(pc,startTime, endTime, step):

    print("Is Thanos Compact Halted?")

    try:
        compactor_data = pc.custom_query('acm_thanos_compact_halted{}')

        compactor_data_df = MetricSnapshotDataFrame(compactor_data)
        compactor_data_df["value"]=compactor_data_df["value"].astype(float)
        compactor_data_df.rename(columns={"value": "CompactorHalted"}, inplace = True)
        print(compactor_data_df[['instance','CompactorHalted']].to_markdown())

        compactor_data_trend = pc.custom_query_range(
        query='acm_thanos_compact_halted{}',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        compactor_data_trend_df = MetricRangeDataFrame(compactor_data_trend)
        compactor_data_trend_df["value"]=compactor_data_trend_df["value"].astype(float)
        compactor_data_trend_df.index= pandas.to_datetime(compactor_data_trend_df.index, unit="s")
        compactor_data_trend_df.rename(columns={"value": "CompactorHalted"}, inplace = True)
        compactor_data_trend_df.plot(title="Thanos Compactor Halted",figsize=(30, 15))
        plt.savefig('../../output/thanos-compact-halted.png')
        saveCSV(compactor_data_trend_df[['CompactorHalted']],'thanos-compact-halted',True)
        plt.close('all')
  
    except Exception as e:
        print(Fore.RED+"Error in gathering thanos compactor halt data: ",e)    
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status 

def thanosRecvSync90(pc,startTime, endTime, step):

    print("Is Thanos receive sync 90th percentile response time")
    sample='histogram_quantile(0.90, sum by(le) (rate(acm_grpc_server_handling_seconds_bucket{grpc_method="RemoteWrite", grpc_type="unary"}[5m])))'


    try:
        recvsync90_data = pc.custom_query(
            query=sample)
        
        recvsync90_data_df = MetricSnapshotDataFrame(recvsync90_data)
        recvsync90_data_df["value"]=recvsync90_data_df["value"].astype(float)
        recvsync90_data_df.rename(columns={"value": "recvsync90"}, inplace = True)
        print(recvsync90_data_df[['recvsync90']].to_markdown())

        recvsync90_data_trend = pc.custom_query_range(
        query=sample,
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        recvsync90_data_trend_df = MetricRangeDataFrame(recvsync90_data_trend)
        recvsync90_data_trend_df["value"]=recvsync90_data_trend_df["value"].astype(float)
        recvsync90_data_trend_df.index= pandas.to_datetime(recvsync90_data_trend_df.index, unit="s")
        recvsync90_data_trend_df.rename(columns={"value": "recvsync90"}, inplace = True)
        recvsync90_data_trend_df.plot(title="Thanos receiver resync 90th percentile",figsize=(30, 15))
        plt.savefig('../../output/thanos-recv-sync-90.png')
        saveCSV(recvsync90_data_trend_df,'thanos-recv-sync-90',True)
        plt.close('all')
  
    except Exception as e:
        print(Fore.RED+"Error in getting Thanos Reciever Sync 90th percentile: ",e)    
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status

def thanosRecvSync95(pc,startTime, endTime, step):

    print("Is Thanos receive sync 95th percentile response time")
    sample='histogram_quantile(0.95, sum by(le) (rate(acm_grpc_server_handling_seconds_bucket{grpc_method="RemoteWrite", grpc_type="unary"}[5m])))'


    try:
        recvsync90_data = pc.custom_query(
            #query='histogram_quantile(0.95, sum by(le) (rate(acm_grpc_server_handling_seconds_bucket{grpc_method="RemoteWrite", grpc_type="unary"}[5m])))')
            query=sample)

        recvsync90_data_df = MetricSnapshotDataFrame(recvsync90_data)
        recvsync90_data_df["value"]=recvsync90_data_df["value"].astype(float)
        recvsync90_data_df.rename(columns={"value": "recvsync95"}, inplace = True)
        print(recvsync90_data_df[['recvsync95']].to_markdown())

        recvsync90_data_trend = pc.custom_query_range(
        #query='histogram_quantile(0.95, sum by(le) (rate(acm_grpc_server_handling_seconds_bucket{grpc_method="RemoteWrite", grpc_type="unary"}[5m])))',
        query=sample,
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        recvsync90_data_trend_df = MetricRangeDataFrame(recvsync90_data_trend)
        recvsync90_data_trend_df["value"]=recvsync90_data_trend_df["value"].astype(float)
        recvsync90_data_trend_df.index= pandas.to_datetime(recvsync90_data_trend_df.index, unit="s")
        recvsync90_data_trend_df.rename(columns={"value": "recvsync95"}, inplace = True)
        recvsync90_data_trend_df.plot(title="Thanos receiver resync 95th percentile",figsize=(30, 15))
        plt.savefig('../../output/thanos-recv-sync-95.png')
        saveCSV(recvsync90_data_trend_df,'thanos-recv-sync-95',True)
        plt.close('all')
  
    except Exception as e:
        print(Fore.RED+"Error in getting Thanos Reciever Sync 95th percentile: ",e)    
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status 

def thanosRecvSync99(pc,startTime, endTime, step):

    print("Is Thanos receive sync 99th percentile response time")
    sample='histogram_quantile(0.99, sum by(le) (rate(acm_grpc_server_handling_seconds_bucket{grpc_method="RemoteWrite", grpc_type="unary"}[5m])))'

    try:
        recvsync90_data = pc.custom_query(
            #query='histogram_quantile(0.99, sum by(le) (rate(acm_grpc_server_handling_seconds_bucket{grpc_method="RemoteWrite", grpc_type="unary"}[5m])))')
            query=sample)

        recvsync90_data_df = MetricSnapshotDataFrame(recvsync90_data)
        recvsync90_data_df["value"]=recvsync90_data_df["value"].astype(float)
        recvsync90_data_df.rename(columns={"value": "recvsync99"}, inplace = True)
        print(recvsync90_data_df[['recvsync99']].to_markdown())

        recvsync90_data_trend = pc.custom_query_range(
        #query='histogram_quantile(0.99, sum by(le) (rate(acm_grpc_server_handling_seconds_bucket{grpc_method="RemoteWrite", grpc_type="unary"}[5m])))',
        query=sample,
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        recvsync90_data_trend_df = MetricRangeDataFrame(recvsync90_data_trend)
        recvsync90_data_trend_df["value"]=recvsync90_data_trend_df["value"].astype(float)
        recvsync90_data_trend_df.index= pandas.to_datetime(recvsync90_data_trend_df.index, unit="s")
        recvsync90_data_trend_df.rename(columns={"value": "recvsync99"}, inplace = True)
        recvsync90_data_trend_df.plot(title="Thanos receiver resync 99th percentile",figsize=(30, 15))
        plt.savefig('../../output/thanos-recv-sync-99.png')
        saveCSV(recvsync90_data_trend_df,'thanos-recv-sync-99',True)
        plt.close('all')
  
    except Exception as e:
        print(Fore.RED+"Error in getting Thanos Reciever Sync 99th percentile: ",e)    
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status

def thanosRecvGrpcError(pc,startTime, endTime, step):

    print("Thanos receive grpc error")
    sample='sum by (grpc_code) (rate(acm_grpc_server_handled_total{grpc_code=~"Unknown|ResourceExhausted|Internal|Unavailable|DataLoss",namespace="open-cluster-management-observability", job=~"observability-thanos-receive-default", grpc_type="unary", grpc_method!="RemoteWrite"}[5m])) / ignoring (grpc_code) group_left() sum(rate(acm_grpc_server_handled_total{namespace="open-cluster-management-observability", job=~"observability-thanos-receive-default", grpc_type="unary", grpc_method!="RemoteWrite"}[5m]))'

    try:
        recvsync90_data = pc.custom_query(
            query=sample)

        recvsync90_data_df = MetricSnapshotDataFrame(recvsync90_data)
        recvsync90_data_df["value"]=recvsync90_data_df["value"].astype(float)
        recvsync90_data_df.rename(columns={"value": "Error"}, inplace = True)
        print(recvsync90_data_df[['grpc_code','Error']].to_markdown())

        recvsync90_data_trend = pc.custom_query_range(
        query=sample,
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        recvsync90_data_trend_df = MetricRangeDataFrame(recvsync90_data_trend)
        recvsync90_data_trend_df["value"]=recvsync90_data_trend_df["value"].astype(float)
        recvsync90_data_trend_df.index= pandas.to_datetime(recvsync90_data_trend_df.index, unit="s")
        recvsync90_data_trend_df =  recvsync90_data_trend_df.pivot( columns='grpc_code',values='value')
        recvsync90_data_trend_df.plot(title="Thanos receiver GRPC Error",figsize=(30, 15))
        plt.savefig('../../output/breakdown/thanos-recv-grpc-error.png')
        saveCSV(recvsync90_data_trend_df,'thanos-recv-grpc-error')
        plt.close('all')
  
    except Exception as e:
        print(Fore.RED+"Error in getting Thanos Reciever GRPC Error: ",e)    
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status
