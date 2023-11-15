from prometheus_api_client import *
#import prometheus_api_client
import datetime
import sys
import numpy as np
import pandas
import utility
from colorama import Fore, Back, Style
import matplotlib.pyplot as plt

def checkAPIServerStatus(startTime, endTime, step):
    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print("API Server Health Check")
    pc=utility.promConnect()
    print("************************************************************************************************")
    print(Style.RESET_ALL)
    status = True

    status=apiServerLatency(pc,startTime, endTime, step)
    status=apiServerObjectCount(pc,startTime, endTime, step)
    status=apiServerObjectCreationCount(pc,startTime, endTime, step)
    status=apiServerRequestByObject(pc,startTime, endTime, step)
    status=apiServerLatencyByObject(pc,startTime, endTime, step)
    
    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print(" API Server Health Check  - ", "PLEASE CHECK to see if the results are concerning!!")
    print("************************************************************************************************")
    print(Style.RESET_ALL)
    return status


def apiServerLatency(pc,startTime, endTime, step):

    print("99th Percentile Latency of API calls to resources - Top 10")

    try:
        apiserver_latency_data = pc.custom_query('topk(10,histogram_quantile(0.99, sum(rate(apiserver_request_duration_seconds_bucket{apiserver="kube-apiserver",subresource!="log",verb!~"WATCH|WATCHLIST|PROXY"}[5m])) by(le,verb)))')
        apiserver_latency_data_df = MetricSnapshotDataFrame(apiserver_latency_data)
        apiserver_latency_data_df["value"]=apiserver_latency_data_df["value"].astype(float)
        apiserver_latency_data_df.rename(columns={"value": "APIServer99PctLatency"}, inplace = True)
        print(apiserver_latency_data_df[['verb','APIServer99PctLatency']].to_markdown())
 
        # not working - need to check
        #query='topk(10,histogram_quantile(0.99, sum(rate(apiserver_request_duration_seconds_bucket{apiserver="kube-apiserver",subresource!="log",verb!~"WATCH|WATCHLIST|PROXY"}[5m])) by(le,verb)))',
        #query='topk(10,histogram_quantile(0.99, sum(rate(apiserver_request_duration_seconds_bucket{apiserver="kube-apiserver",subresource!="log",verb!~"WATCH|WATCHLIST|PROXY"}[5m])) by(le,resource)))',
        #query='histogram_quantile(0.99, sum(rate(apiserver_request_duration_seconds_bucket{apiserver="kube-apiserver",subresource!="log",verb!~"WATCH|WATCHLIST|PROXY"}[5m])) by(le))',
         
        """     
        apiserver_data_trend = pc.custom_query_range(
         query='histogram_quantile(0.99, sum(rate(apiserver_request_duration_seconds_bucket{apiserver="kube-apiserver",subresource!="log",verb!~"WATCH|WATCHLIST|PROXY"}[5m])) by(le))',
             start_time=startTime,
             end_time=endTime,
             step=step,
         )

        apiserver_data_trend_df = MetricRangeDataFrame(apiserver_data_trend)
        apiserver_data_trend_df["value"]= apiserver_data_trend_df["value"].astype(float)
        apiserver_data_trend_df.index= pandas.to_datetime(apiserver_data_trend_df.index, unit="s")
        #apiserver_data_trend_df = apiserver_data_trend_df.pivot( columns='verb',values='value')
        apiserver_data_trend_df.plot(title="API Server Latency",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/breakdown/api-server-latency.png')  
        """       
    except Exception as e:
        print(Fore.RED+"Error in getting 99th Percentile Latency of API calls to resources - Top 10",e)
        print(Style.RESET_ALL)

    print("=============================================")
    
    status=True
    return status  

def apiServerObjectCount(pc,startTime, endTime, step) : 

    print("Checking API Server Object Count")

    try:
        apiserver_obj_count = pc.custom_query('topk(10,max(apiserver_storage_objects{resource!="events"}) by (resource))')
        apiserver_obj_count_df = MetricSnapshotDataFrame(apiserver_obj_count)
        apiserver_obj_count_df["value"]=apiserver_obj_count_df["value"].astype(float)
        apiserver_obj_count_df.rename(columns={"value": "APIServerObjCount"}, inplace = True)
        print(apiserver_obj_count_df[['resource','APIServerObjCount']].to_markdown())

        apiserver_data_trend = pc.custom_query_range(
        query='topk(10,max(apiserver_storage_objects{resource!="events"}) by (resource))',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        apiserver_data_trend_df = MetricRangeDataFrame(apiserver_data_trend)
        apiserver_data_trend_df["value"]=apiserver_data_trend_df["value"].astype(float)
        apiserver_data_trend_df.index= pandas.to_datetime(apiserver_data_trend_df.index, unit="s")
        apiserver_data_trend_df =  apiserver_data_trend_df.pivot( columns='resource',values='value')
        apiserver_data_trend_df.plot(title="Trend of API Server Object Count",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/breakdown/apiserver-resource-count.png')
        utility.saveCSV(apiserver_data_trend_df, "apiserver-resource-count")
        plt.close('all')
    except Exception as e:
        print(Fore.RED+"Error in getting API Server Object Count: ",e)
        print(Style.RESET_ALL)

    print("=============================================")

def apiServerObjectCreationCount(pc,startTime, endTime, step) : 

    print("Checking API Server Object Creation Count")

    try:
        apiserver_obj_count = pc.custom_query('topk(10, sum(delta(apiserver_storage_objects{resource!="events"}[5m])>0) by (resource))')
        apiserver_obj_count_df = MetricSnapshotDataFrame(apiserver_obj_count)
        apiserver_obj_count_df["value"]=apiserver_obj_count_df["value"].astype(float)
        apiserver_obj_count_df.rename(columns={"value": "APIServerObjCount"}, inplace = True)
        print(apiserver_obj_count_df[['resource','APIServerObjCount']].to_markdown())

        apiserver_data_trend = pc.custom_query_range(
        query='topk(10, sum(delta(apiserver_storage_objects{resource!="events"}[5m])>0) by (resource))',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        apiserver_data_trend_df = MetricRangeDataFrame(apiserver_data_trend)
        apiserver_data_trend_df["value"]=apiserver_data_trend_df["value"].astype(float)
        apiserver_data_trend_df.index= pandas.to_datetime(apiserver_data_trend_df.index, unit="s")
        apiserver_data_trend_df =  apiserver_data_trend_df.pivot( columns='resource',values='value')
        apiserver_data_trend_df.plot(title="Trend of API Server Object Creation Count",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/breakdown/apiserver-resource-creation-count.png')
        utility.saveCSV(apiserver_data_trend_df, "apiserver-resource-creation-count")
        plt.close('all')
    except Exception as e:
        print(Fore.RED+"Error in getting API Server Object Creation Count or No new objects created ...",e)
        print(Style.RESET_ALL)

    print("=============================================")

def apiServerRequestByObject(pc,startTime, endTime, step) : 

    print("Checking API Server Request Count by Object")

    try:
        apiserver_obj_count = pc.custom_query('topk(20, sum(rate(apiserver_request_total{apiserver="kube-apiserver"}[5m])) by(resource))')
        apiserver_obj_count_df = MetricSnapshotDataFrame(apiserver_obj_count)
        apiserver_obj_count_df["value"]=apiserver_obj_count_df["value"].astype(float)
        apiserver_obj_count_df.rename(columns={"value": "APIServerObjCount"}, inplace = True)
        print(apiserver_obj_count_df[['resource','APIServerObjCount']].to_markdown())

        apiserver_data_trend = pc.custom_query_range(
        query='topk(20, sum(rate(apiserver_request_total{apiserver="kube-apiserver"}[5m])) by(resource))',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        apiserver_data_trend_df = MetricRangeDataFrame(apiserver_data_trend)
        apiserver_data_trend_df["value"]=apiserver_data_trend_df["value"].astype(float)
        apiserver_data_trend_df.index= pandas.to_datetime(apiserver_data_trend_df.index, unit="s")
        apiserver_data_trend_df =  apiserver_data_trend_df.pivot( columns='resource',values='value')
        apiserver_data_trend_df.plot(title="Trend of API Server Request Count by Object",figsize=(30, 15))
        plt.savefig(utility.inspector_dir + '/breakdown/apiserver-request-count-by-object.png')
        utility.saveCSV(apiserver_data_trend_df, "apiserver-request-count-by-object")
        plt.close('all')
    except Exception as e:
        print(Fore.RED+"Error in getting API Server Request Count by Object: ",e)
        print(Style.RESET_ALL)

    print("=============================================")   

def apiServerLatencyByObject(pc,startTime, endTime, step) : 

    print("Checking API Server Latency Value by Object")

    try:
        apiserver_obj_count = pc.custom_query('topk(10, histogram_quantile(0.99, sum(rate(apiserver_request_duration_seconds_bucket{apiserver="kube-apiserver",subresource!="log",verb!~"WATCH|WATCHLIST|PROXY"}[5m])) by(resource,le)))')
        apiserver_obj_count_df = MetricSnapshotDataFrame(apiserver_obj_count)
        apiserver_obj_count_df["value"]=apiserver_obj_count_df["value"].astype(float)
        apiserver_obj_count_df.rename(columns={"value": "APILatency"}, inplace = True)
        print(apiserver_obj_count_df[['resource','APILatency']].to_markdown())

        # Need to fix this
        # apiserver_data_trend = pc.custom_query_range(
        # query='topk(3, histogram_quantile(0.99, sum(rate(apiserver_request_duration_seconds_bucket{apiserver="kube-apiserver",subresource!="log",verb!~"WATCH|WATCHLIST|PROXY"}[5m])) by(resource,le)))',
        #     start_time=startTime,
        #     end_time=endTime,
        #     step=step,
        # )

        # apiserver_data_trend_df = MetricRangeDataFrame(apiserver_data_trend)
        # apiserver_data_trend_df["value"]=apiserver_data_trend_df["value"].astype(float)
        # apiserver_data_trend_df.index= pandas.to_datetime(apiserver_data_trend_df.index, unit="s")
        # apiserver_data_trend_df =  apiserver_data_trend_df.pivot( columns='resource',values='value')
        # apiserver_data_trend_df.plot(title="Trend of API Server Latency by Object",figsize=(30, 15))
        # plt.savefig(utility.inspector_dir + '/breakdown/apiserver-latency-by-object.png')
    except Exception as e:
        print(Fore.RED+"Error in getting API Server Latency by Object: ",e)
        print(Style.RESET_ALL)

    print("=============================================")        

