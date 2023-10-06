from prometheus_api_client import *
import datetime
import sys
import numpy as np
import pandas
from utility import *
from colorama import Fore, Back, Style
import matplotlib.pyplot as plt

def checkMemoryUsage(startTime, endTime, step):
    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print("Checking Memory Usage across the cluster")
    pc=promConnect()
    print("************************************************************************************************")
    print(Style.RESET_ALL)
    status = True

    status=clusterMemCapacity(pc,startTime, endTime, step)
    status=clusterMemUsed(pc,startTime, endTime, step)
    status=clusterMemPctUsed(pc,startTime, endTime, step)
    #status=clusterMemUsage(pc,startTime, endTime, step)
    status=nodeMemUsage(pc,startTime, endTime, step)
    status=kubeAPIMemUsageRSS(pc,startTime, endTime, step)
    status=ACMMemUsageRSS(pc,startTime, endTime, step)
    status=ACMDetailMemUsageRSS(pc,startTime, endTime, step)
    status=OtherMemUsageRSS(pc,startTime, endTime, step)
    status=OtherDetailMemUsageRSS(pc,startTime, endTime, step)
    status=kubeAPIMemUsageWSS(pc,startTime, endTime, step)
    status=ACMMemUsageWSS(pc,startTime, endTime, step)
    status=ACMDetailMemUsageWSS(pc,startTime, endTime, step)
    status=OtherMemUsageWSS(pc,startTime, endTime, step)
    status=OtherDetailMemUsageWSS(pc,startTime, endTime, step)
    status=ACMObsMemUsageRSS(pc,startTime,endTime, step)
    status=ACMObsMemUsageWSS(pc,startTime,endTime, step)
    status=ACMOtherMemUsageRSS(pc,startTime,endTime, step)
    status=ACMOtherMemUsageWSS(pc,startTime,endTime, step)
    status=ACMObsDetailMemUsageRSS(pc,startTime, endTime, step)
    status=ACMObsDetailMemUsageWSS(pc,startTime, endTime, step)
    status=ACMObsRecvMemUsageRSS(pc,startTime, endTime, step)
    status=ACMObsRecvMemUsageWSS(pc,startTime, endTime, step)
    status=ACMOCMDetailMemUsageRSS(pc,startTime, endTime, step)
    status=ACMOCMDetailMemUsageWSS(pc,startTime, endTime, step)
    status=ACMSrcPGvMemUsageRSS(pc,startTime, endTime, step)
    status=ACMSrcIdxvMemUsageRSS(pc,startTime, endTime, step)
    status=ACMOSrcPGMemUsageWSS(pc,startTime, endTime, step)
    status=ACMOSrcIdxMemUsageWSS(pc,startTime, endTime, step)


    

    
    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print("Memory Health Check  - ", "PLEASE CHECK to see if the results are concerning!! ")
    print("************************************************************************************************")
    print(Style.RESET_ALL)
    return status
     
def clusterMemCapacity(pc,startTime, endTime, step):

    # Refer OCP Dashboard - Kubernnetes / Compute Resources / Cluster
    # Graph - Memory Utilization
    # Query - 1 - sum(:node_memory_MemAvailable_bytes:sum{cluster=""}) / sum(node_memory_MemTotal_bytes{job="node-exporter",cluster=""})
    print("Total Cluster Memory Capacity GB")

    try:
        node_cpu = pc.custom_query('sum(node_memory_MemTotal_bytes{job="node-exporter",cluster=""})/(1024*1024*1024)')

        node_cpu_df = MetricSnapshotDataFrame(node_cpu)
        node_cpu_df["value"]=node_cpu_df["value"].astype(float)
        node_cpu_df.rename(columns={"value": "ClusterMemCapacityGB"}, inplace = True)
        print(node_cpu_df[['ClusterMemCapacityGB']].to_markdown())

        node_cpu_trend = pc.custom_query_range(
        query='sum(node_memory_MemTotal_bytes{job="node-exporter",cluster=""})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        node_cpu_trend_df = MetricRangeDataFrame(node_cpu_trend)
        node_cpu_trend_df["value"]=node_cpu_trend_df["value"].astype(float)
        node_cpu_trend_df.index= pandas.to_datetime(node_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        node_cpu_trend_df.rename(columns={"value": "ClusterMemCapacityGB"}, inplace = True)
        node_cpu_trend_df.plot(title="Cluster Memory Capacity GB",figsize=(30, 15))
        plt.savefig('../../output/cluster-mem-capacity.png')
        saveCSV(node_cpu_trend_df,"cluster-mem-capacity",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting memory Capacity for cluster: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def clusterMemUsed(pc,startTime, endTime, step):
    
    # Refer OCP Dashboard - Kubernnetes / Compute Resources / Cluster
    # Graph - Memory Usage (w/o cache)
    # Query - sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!=""}) by (namespace)
    
    # Was used originally but changing it to use

    # Refer OCP Dashboard - Kubernnetes / Compute Resources / Cluster
    # Graph - Memory Utilization
    # Query - 1 - sum(:node_memory_MemAvailable_bytes:sum{cluster=""}) / sum(node_memory_MemTotal_bytes{job="node-exporter",cluster=""})
    print("Total Cluster Memory usage GB")

    try:
        node_cpu = pc.custom_query('(sum(node_memory_MemTotal_bytes{job="node-exporter",cluster=""}) -sum(:node_memory_MemAvailable_bytes:sum{cluster=""}) )/(1024*1024*1024)')

        node_cpu_df = MetricSnapshotDataFrame(node_cpu)
        node_cpu_df["value"]=node_cpu_df["value"].astype(float)
        node_cpu_df.rename(columns={"value": "ClusterMemUsageGB"}, inplace = True)
        print(node_cpu_df[['ClusterMemUsageGB']].to_markdown())

        node_cpu_trend = pc.custom_query_range(
        query='(sum(node_memory_MemTotal_bytes{job="node-exporter",cluster=""}) -sum(:node_memory_MemAvailable_bytes:sum{cluster=""}) )/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        node_cpu_trend_df = MetricRangeDataFrame(node_cpu_trend)
        node_cpu_trend_df["value"]=node_cpu_trend_df["value"].astype(float)
        node_cpu_trend_df.index= pandas.to_datetime(node_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        node_cpu_trend_df.rename(columns={"value": "ClusterMemUsageGB"}, inplace = True)
        node_cpu_trend_df.plot(title="Cluster Memory usage GB",figsize=(30, 15))
        plt.savefig('../../output/cluster-mem-usage.png')
        saveCSV(node_cpu_trend_df,"cluster-mem-usage",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting memory for cluster: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def clusterMemPctUsed(pc,startTime, endTime, step):

    # Refer OCP Dashboard - Kubernnetes / Compute Resources / Cluster
    # Graph - Memory Utilization
    # Query - 1 - sum(:node_memory_MemAvailable_bytes:sum{cluster=""}) / sum(node_memory_MemTotal_bytes{job="node-exporter",cluster=""})
    print("Total Cluster Memory Pct usage")

    try:
        node_cpu = pc.custom_query('(1 - sum(:node_memory_MemAvailable_bytes:sum{cluster=""}) / sum(node_memory_MemTotal_bytes{job="node-exporter",cluster=""}))*100')

        node_cpu_df = MetricSnapshotDataFrame(node_cpu)
        node_cpu_df["value"]=node_cpu_df["value"].astype(float)
        node_cpu_df.rename(columns={"value": "ClusterMemUsagePct"}, inplace = True)
        print(node_cpu_df[['ClusterMemUsagePct']].to_markdown())

        node_cpu_trend = pc.custom_query_range(
        query='(1 - sum(:node_memory_MemAvailable_bytes:sum{cluster=""}) / sum(node_memory_MemTotal_bytes{job="node-exporter",cluster=""}))*100',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        node_cpu_trend_df = MetricRangeDataFrame(node_cpu_trend)
        node_cpu_trend_df["value"]=node_cpu_trend_df["value"].astype(float)
        node_cpu_trend_df.index= pandas.to_datetime(node_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        node_cpu_trend_df.rename(columns={"value": "ClusterMemUsagePct"}, inplace = True)
        node_cpu_trend_df.plot(title="Cluster Memory Pct usage",figsize=(30, 15))
        plt.savefig('../../output/cluster-mem-pct-usage.png')
        saveCSV(node_cpu_trend_df,"cluster-mem-pct-usage",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting memory pct for cluster: ",e)    
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status

def nodeMemUsage(pc,startTime, endTime, step):

    # Refer OCP Dashboard - Node Exporter / Use Method/ Node
    # Graph - Memory Utilization
    # Query - 1 - instance:node_memory_utilisation:ratio{job="node-exporter", instance="xyz", cluster=""} != 0
    # decompose the recordiong rules to get the query
    #       - expr: |
        #   1 - (
        #     (
        #       node_memory_MemAvailable_bytes{job="node-exporter"}
        #       or
        #       (
        #         node_memory_Buffers_bytes{job="node-exporter"}
        #         +
        #         node_memory_Cached_bytes{job="node-exporter"}
        #         +
        #         node_memory_MemFree_bytes{job="node-exporter"}
        #         +
        #         node_memory_Slab_bytes{job="node-exporter"}
        #       )
        #     )
        #   /
        #     node_memory_MemTotal_bytes{job="node-exporter"}
        #   )
        # record: instance:node_memory_utilisation:ratio
    # do not derive node statistics as an aggregate of container statistics
    
    print("Memory Usage across Nodes GB")

    sample = '(node_memory_MemTotal_bytes{job="node-exporter"} - ( node_memory_MemAvailable_bytes{job="node-exporter"} or ( node_memory_Buffers_bytes{job="node-exporter"} + node_memory_Cached_bytes{job="node-exporter"} + node_memory_MemFree_bytes{job="node-exporter"} + node_memory_Slab_bytes{job="node-exporter"} ) ))/(1024*1024*1024)'

    try:
        node_cpu = pc.custom_query(sample)

        node_cpu_df = MetricSnapshotDataFrame(node_cpu)
        node_cpu_df["value"]=node_cpu_df["value"].astype(float)
        node_cpu_df.rename(columns={"value": "NodeMemUsageGB"}, inplace = True)
        print(node_cpu_df[['instance','NodeMemUsageGB']].to_markdown())

        node_cpu_trend = pc.custom_query_range(
        query=sample,
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        node_cpu_trend_df = MetricRangeDataFrame(node_cpu_trend)
        node_cpu_trend_df["value"]=node_cpu_trend_df["value"].astype(float)
        node_cpu_trend_df.index= pandas.to_datetime(node_cpu_trend_df.index, unit="s")
        node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='instance',values='value')
        node_cpu_trend_df.rename(columns={"value": "NodeMemUsageGB"}, inplace = True)
        node_cpu_trend_df.plot(title="Memory Usage across Nodes GB",figsize=(30, 15))
        plt.savefig('../../output/breakdown/node-mem-usage.png')
        saveCSV(node_cpu_trend_df,"node-mem-usage")
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting memory usage across Nodes: ",e) 
        print(Style.RESET_ALL)   
    print("=============================================")
   
    status=True
    return status   

def kubeAPIMemUsageRSS(pc,startTime, endTime, step):

    print("Total Kube API Server Memory (rss) usage GB")

    try:
        kubeapi_cpu = pc.custom_query('sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace=~"openshift-kube-apiserver|openshift-etcd"})/(1024*1024*1024)')

        kubeapi_cpu_df = MetricSnapshotDataFrame(kubeapi_cpu)
        kubeapi_cpu_df["value"]=kubeapi_cpu_df["value"].astype(float)
        kubeapi_cpu_df.rename(columns={"value": "KubeAPIMemUsageRSSGB"}, inplace = True)
        print(kubeapi_cpu_df[['KubeAPIMemUsageRSSGB']].to_markdown())

        kubeapi_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace=~"openshift-kube-apiserver|openshift-etcd"})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        kubeapi_cpu_trend_df = MetricRangeDataFrame(kubeapi_cpu_trend)
        kubeapi_cpu_trend_df["value"]=kubeapi_cpu_trend_df["value"].astype(float)
        kubeapi_cpu_trend_df.index= pandas.to_datetime(kubeapi_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        kubeapi_cpu_trend_df.rename(columns={"value": "KubeAPIMemUsageRSSGB"}, inplace = True)
        kubeapi_cpu_trend_df.plot(title="Kube API Server Memory (rss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/kubeapi-mem-usage-rss.png')
        saveCSV(kubeapi_cpu_trend_df,"kubeapi-mem-usage-rss",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting memory (rss) for Kube API Server: ",e)    
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status  

def ACMMemUsageRSS(pc,startTime, endTime, step):

    print("Total ACM Memory (rss) usage GB")

    try:
        acm_cpu = pc.custom_query('sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace=~"multicluster-engine|open-cluster-.+"})/(1024*1024*1024)')

        acm_cpu_df = MetricSnapshotDataFrame(acm_cpu)
        acm_cpu_df["value"]=acm_cpu_df["value"].astype(float)
        acm_cpu_df.rename(columns={"value": "ACMMemUsageRSSGB"}, inplace = True)
        print(acm_cpu_df[['ACMMemUsageRSSGB']].to_markdown())

        acm_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace=~"multicluster-engine|open-cluster-.+"})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_cpu_trend_df = MetricRangeDataFrame(acm_cpu_trend)
        acm_cpu_trend_df["value"]=acm_cpu_trend_df["value"].astype(float)
        acm_cpu_trend_df.index= pandas.to_datetime(acm_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        acm_cpu_trend_df.rename(columns={"value": "ACMMemUsageRSSGB"}, inplace = True)
        acm_cpu_trend_df.plot(title="ACM Memory (rss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/acm-mem-usage-rss.png')
        saveCSV(acm_cpu_trend_df,"acm-mem-usage-rss",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting Memory (rss) for ACM: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def ACMDetailMemUsageRSS(pc,startTime, endTime, step):

    print("Detailed ACM Memory (rss) usage GB")

    try:
        acm_detail_cpu = pc.custom_query('(sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace=~"multicluster-engine|open-cluster-.+"}) by (namespace))/(1024*1024*1024)')

        acm_detail_cpu_df = MetricSnapshotDataFrame(acm_detail_cpu)
        acm_detail_cpu_df["value"]=acm_detail_cpu_df["value"].astype(float)
        acm_detail_cpu_df.rename(columns={"value": "ACMDetailMemUsageRSSGB"}, inplace = True)
        print(acm_detail_cpu_df[['namespace','ACMDetailMemUsageRSSGB']].to_markdown())

        acm_detail_cpu_trend = pc.custom_query_range(
        query='(sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace=~"multicluster-engine|open-cluster-.+"}) by (namespace))/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_detail_cpu_trend_df = MetricRangeDataFrame(acm_detail_cpu_trend)
        acm_detail_cpu_trend_df["value"]=acm_detail_cpu_trend_df["value"].astype(float)
        acm_detail_cpu_trend_df.index= pandas.to_datetime(acm_detail_cpu_trend_df.index, unit="s")
        acm_detail_cpu_trend_df =  acm_detail_cpu_trend_df.pivot( columns='namespace',values='value')
        acm_detail_cpu_trend_df.plot(title="ACM Detailed Memory (rss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/breakdown/acm-detail-mem-usage-rss.png')
        saveCSV(acm_detail_cpu_trend_df,"acm-detail-mem-usage-rss")
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting memory (rss) details for ACM: ",e)    
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status

def OtherMemUsageRSS(pc,startTime, endTime, step):

    print("Total Memory (rss) usage for Others GB")

    try:
        acm_cpu = pc.custom_query('sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace!~"multicluster-engine|open-cluster-.+|openshift-kube-apiserver|openshift-etcd"})/(1024*1024*1024)')

        acm_cpu_df = MetricSnapshotDataFrame(acm_cpu)
        acm_cpu_df["value"]=acm_cpu_df["value"].astype(float)
        acm_cpu_df.rename(columns={"value": "OtherMemUsageRSSGB"}, inplace = True)
        print(acm_cpu_df[['OtherMemUsageRSSGB']].to_markdown())

        acm_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace!~"multicluster-engine|open-cluster-.+|openshift-kube-apiserver|openshift-etcd"})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_cpu_trend_df = MetricRangeDataFrame(acm_cpu_trend)
        acm_cpu_trend_df["value"]=acm_cpu_trend_df["value"].astype(float)
        acm_cpu_trend_df.index= pandas.to_datetime(acm_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        acm_cpu_trend_df.rename(columns={"value": "OtherMemUsageRSSGB"}, inplace = True)
        acm_cpu_trend_df.plot(title="Other Memory usage GB",figsize=(30, 15))
        plt.savefig('../../output/other-mem-usage-rss.png')
        saveCSV(acm_cpu_trend_df,"other-mem-usage-rss",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting Memory (rss) for Other: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def OtherDetailMemUsageRSS(pc,startTime, endTime, step):

    print("Total Detail Memory (rss) usage for Others GB")

    try:
        acm_cpu = pc.custom_query('sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace!~"multicluster-engine|open-cluster-.+|openshift-kube-apiserver|openshift-etcd"}) by (namespace)/(1024*1024*1024)')

        acm_cpu_df = MetricSnapshotDataFrame(acm_cpu)
        acm_cpu_df["value"]=acm_cpu_df["value"].astype(float)
        acm_cpu_df.rename(columns={"value": "OtherDetailMemUsageRSSGB"}, inplace = True)
        print(acm_cpu_df[['namespace','OtherDetailMemUsageRSSGB']].to_markdown())

        acm_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace!~"multicluster-engine|open-cluster-.+|openshift-kube-apiserver|openshift-etcd"}) by (namespace)/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_cpu_trend_df = MetricRangeDataFrame(acm_cpu_trend)
        acm_cpu_trend_df["value"]=acm_cpu_trend_df["value"].astype(float)
        acm_cpu_trend_df.index= pandas.to_datetime(acm_cpu_trend_df.index, unit="s")
        acm_cpu_trend_df =  acm_cpu_trend_df.pivot( columns='namespace',values='value')
        acm_cpu_trend_df.rename(columns={"value": "OtherDetailMemUsageRSSGB"}, inplace = True)
        acm_cpu_trend_df.plot(title="Other Detail Memory (rss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/breakdown/other-detail-mem-usage-rss.png')
        saveCSV(acm_cpu_trend_df,"other-detail-mem-usage-rss")
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting Detail Memory (rss) for Other: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def kubeAPIMemUsageWSS(pc,startTime, endTime, step):

    print("Total Kube API Server Memory (wss) usage GB")

    try:
        kubeapi_cpu = pc.custom_query('sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace=~"openshift-kube-apiserver|openshift-etcd"})/(1024*1024*1024)')

        kubeapi_cpu_df = MetricSnapshotDataFrame(kubeapi_cpu)
        kubeapi_cpu_df["value"]=kubeapi_cpu_df["value"].astype(float)
        kubeapi_cpu_df.rename(columns={"value": "KubeAPIMemUsageWSSGB"}, inplace = True)
        print(kubeapi_cpu_df[['KubeAPIMemUsageWSSGB']].to_markdown())

        kubeapi_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace=~"openshift-kube-apiserver|openshift-etcd"})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        kubeapi_cpu_trend_df = MetricRangeDataFrame(kubeapi_cpu_trend)
        kubeapi_cpu_trend_df["value"]=kubeapi_cpu_trend_df["value"].astype(float)
        kubeapi_cpu_trend_df.index= pandas.to_datetime(kubeapi_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        kubeapi_cpu_trend_df.rename(columns={"value": "KubeAPIMemUsageWSSGB"}, inplace = True)
        kubeapi_cpu_trend_df.plot(title="Kube API Server Memory (wss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/kubeapi-mem-usage-wss.png')
        saveCSV(kubeapi_cpu_trend_df,"kubeapi-mem-usage-wss",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting memory (wss) for Kube API Server: ",e)    
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status  

def ACMMemUsageWSS(pc,startTime, endTime, step):

    print("Total ACM Memory (wss) usage GB")

    try:
        acm_cpu = pc.custom_query('sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace=~"multicluster-engine|open-cluster-.+"})/(1024*1024*1024)')

        acm_cpu_df = MetricSnapshotDataFrame(acm_cpu)
        acm_cpu_df["value"]=acm_cpu_df["value"].astype(float)
        acm_cpu_df.rename(columns={"value": "ACMMemUsageWSSGB"}, inplace = True)
        print(acm_cpu_df[['ACMMemUsageWSSGB']].to_markdown())

        acm_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace=~"multicluster-engine|open-cluster-.+"})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_cpu_trend_df = MetricRangeDataFrame(acm_cpu_trend)
        acm_cpu_trend_df["value"]=acm_cpu_trend_df["value"].astype(float)
        acm_cpu_trend_df.index= pandas.to_datetime(acm_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        acm_cpu_trend_df.rename(columns={"value": "ACMMemUsageWSSGB"}, inplace = True)
        acm_cpu_trend_df.plot(title="ACM Memory (wss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/acm-mem-usage-wss.png')
        saveCSV(acm_cpu_trend_df,"acm-mem-usage-wss",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting Memory (wss) for ACM: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def ACMDetailMemUsageWSS(pc,startTime, endTime, step):

    print("Detailed ACM Memory (wss) usage GB")

    try:
        acm_detail_cpu = pc.custom_query('(sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace=~"multicluster-engine|open-cluster-.+"}) by (namespace))/(1024*1024*1024)')

        acm_detail_cpu_df = MetricSnapshotDataFrame(acm_detail_cpu)
        acm_detail_cpu_df["value"]=acm_detail_cpu_df["value"].astype(float)
        acm_detail_cpu_df.rename(columns={"value": "ACMDetailMemUsageWSSGB"}, inplace = True)
        print(acm_detail_cpu_df[['namespace','ACMDetailMemUsageWSSGB']].to_markdown())

        acm_detail_cpu_trend = pc.custom_query_range(
        query='(sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace=~"multicluster-engine|open-cluster-.+"}) by (namespace))/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_detail_cpu_trend_df = MetricRangeDataFrame(acm_detail_cpu_trend)
        acm_detail_cpu_trend_df["value"]=acm_detail_cpu_trend_df["value"].astype(float)
        acm_detail_cpu_trend_df.index= pandas.to_datetime(acm_detail_cpu_trend_df.index, unit="s")
        acm_detail_cpu_trend_df =  acm_detail_cpu_trend_df.pivot( columns='namespace',values='value')
        acm_detail_cpu_trend_df.plot(title="ACM Detailed Memory (wss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/breakdown/acm-detail-mem-usage-wss.png')
        saveCSV(acm_detail_cpu_trend_df,"acm-detail-mem-usage-wss")
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting memory (wss) details for ACM: ",e)    
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status

def OtherMemUsageWSS(pc,startTime, endTime, step):

    print("Total Memory (wss) usage for Others GB")

    try:
        acm_cpu = pc.custom_query('sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace!~"multicluster-engine|open-cluster-.+|openshift-kube-apiserver|openshift-etcd"})/(1024*1024*1024)')

        acm_cpu_df = MetricSnapshotDataFrame(acm_cpu)
        acm_cpu_df["value"]=acm_cpu_df["value"].astype(float)
        acm_cpu_df.rename(columns={"value": "OtherMemUsageWSSGB"}, inplace = True)
        print(acm_cpu_df[['OtherMemUsageWSSGB']].to_markdown())

        acm_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace!~"multicluster-engine|open-cluster-.+|openshift-kube-apiserver|openshift-etcd"})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_cpu_trend_df = MetricRangeDataFrame(acm_cpu_trend)
        acm_cpu_trend_df["value"]=acm_cpu_trend_df["value"].astype(float)
        acm_cpu_trend_df.index= pandas.to_datetime(acm_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        acm_cpu_trend_df.rename(columns={"value": "OtherMemUsageWSSGB"}, inplace = True)
        acm_cpu_trend_df.plot(title="Other Memory usage GB",figsize=(30, 15))
        plt.savefig('../../output/other-mem-usage-wss.png')
        saveCSV(acm_cpu_trend_df,"other-mem-usage-wss",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting Memory (wss) for Other: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def OtherDetailMemUsageWSS(pc,startTime, endTime, step):

    print("Total Detail Memory (wss) usage for Others GB")

    try:
        acm_cpu = pc.custom_query('sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace!~"multicluster-engine|open-cluster-.+|openshift-kube-apiserver|openshift-etcd"}) by (namespace)/(1024*1024*1024)')

        acm_cpu_df = MetricSnapshotDataFrame(acm_cpu)
        acm_cpu_df["value"]=acm_cpu_df["value"].astype(float)
        acm_cpu_df.rename(columns={"value": "OtherDetailMemUsageWSSGB"}, inplace = True)
        print(acm_cpu_df[['namespace','OtherDetailMemUsageWSSGB']].to_markdown())

        acm_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace!~"multicluster-engine|open-cluster-.+|openshift-kube-apiserver|openshift-etcd"}) by (namespace)/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_cpu_trend_df = MetricRangeDataFrame(acm_cpu_trend)
        acm_cpu_trend_df["value"]=acm_cpu_trend_df["value"].astype(float)
        acm_cpu_trend_df.index= pandas.to_datetime(acm_cpu_trend_df.index, unit="s")
        acm_cpu_trend_df =  acm_cpu_trend_df.pivot( columns='namespace',values='value')
        acm_cpu_trend_df.rename(columns={"value": "OtherDetailMemUsageWSSGB"}, inplace = True)
        acm_cpu_trend_df.plot(title="Other Detail Memory (wss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/breakdown/other-detail-mem-usage-wss.png')
        saveCSV(acm_cpu_trend_df,"other-detail-mem-usage-wss")
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting Detail Memory (wss) for Other: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def ACMObsMemUsageRSS(pc,startTime, endTime, step):

    print("Total ACM Obs Memory (rss) usage GB")

    try:
        acm_cpu = pc.custom_query('sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace="open-cluster-management-observability"})/(1024*1024*1024)')

        acm_cpu_df = MetricSnapshotDataFrame(acm_cpu)
        acm_cpu_df["value"]=acm_cpu_df["value"].astype(float)
        acm_cpu_df.rename(columns={"value": "ACMObsMemUsageRSSGB"}, inplace = True)
        print(acm_cpu_df[['ACMObsMemUsageRSSGB']].to_markdown())

        acm_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace="open-cluster-management-observability"})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_cpu_trend_df = MetricRangeDataFrame(acm_cpu_trend)
        acm_cpu_trend_df["value"]=acm_cpu_trend_df["value"].astype(float)
        acm_cpu_trend_df.index= pandas.to_datetime(acm_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        acm_cpu_trend_df.rename(columns={"value": "ACMObsMemUsageRSSGB"}, inplace = True)
        acm_cpu_trend_df.plot(title="ACM Obs Memory (rss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/acm-obs-mem-usage-rss.png')
        saveCSV(acm_cpu_trend_df,"acm-obs-mem-usage-rss",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting Memory (rss) for ACM Obs: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def ACMObsMemUsageWSS(pc,startTime, endTime, step):

    print("Total ACM Obs Memory (wss) usage GB")

    try:
        acm_cpu = pc.custom_query('sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace="open-cluster-management-observability"})/(1024*1024*1024)')

        acm_cpu_df = MetricSnapshotDataFrame(acm_cpu)
        acm_cpu_df["value"]=acm_cpu_df["value"].astype(float)
        acm_cpu_df.rename(columns={"value": "ACMObsMemUsageWSSGB"}, inplace = True)
        print(acm_cpu_df[['ACMObsMemUsageWSSGB']].to_markdown())

        acm_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace="open-cluster-management-observability"})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_cpu_trend_df = MetricRangeDataFrame(acm_cpu_trend)
        acm_cpu_trend_df["value"]=acm_cpu_trend_df["value"].astype(float)
        acm_cpu_trend_df.index= pandas.to_datetime(acm_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        acm_cpu_trend_df.rename(columns={"value": "ACMObsMemUsageWSSGB"}, inplace = True)
        acm_cpu_trend_df.plot(title="ACM Obs Memory (wss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/acm-obs-mem-usage-wss.png')
        saveCSV(acm_cpu_trend_df,"acm-obs-mem-usage-wss",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting Memory (wss) for ACM Obs: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def ACMOtherMemUsageRSS(pc,startTime, endTime, step):

    print("Total ACM Others Memory (rss) usage GB")

    try:
        acm_cpu = pc.custom_query('sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace=~"multicluster-engine|open-cluster-management|open-cluster-management-agent.+|open-cluster-management-hub|open-cluster-management-addon.+"})/(1024*1024*1024)')

        acm_cpu_df = MetricSnapshotDataFrame(acm_cpu)
        acm_cpu_df["value"]=acm_cpu_df["value"].astype(float)
        acm_cpu_df.rename(columns={"value": "ACMOthMemUsageRSSGB"}, inplace = True)
        print(acm_cpu_df[['ACMOthMemUsageRSSGB']].to_markdown())

        acm_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace=~"multicluster-engine|open-cluster-management-agent.+|open-cluster-management-hub|open-cluster-management-addon.+"})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_cpu_trend_df = MetricRangeDataFrame(acm_cpu_trend)
        acm_cpu_trend_df["value"]=acm_cpu_trend_df["value"].astype(float)
        acm_cpu_trend_df.index= pandas.to_datetime(acm_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        acm_cpu_trend_df.rename(columns={"value": "ACMOthMemUsageRSSGB"}, inplace = True)
        acm_cpu_trend_df.plot(title="ACM Other Memory (rss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/acm-oth-mem-usage-rss.png')
        saveCSV(acm_cpu_trend_df,"acm-oth-mem-usage-rss",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting Memory (rss) for ACM Others: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def ACMOtherMemUsageWSS(pc,startTime, endTime, step):

    print("Total ACM Other Memory (wss) usage GB")

    try:
        acm_cpu = pc.custom_query('sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace=~"multicluster-engine|open-cluster-management-agent.+|open-cluster-management-hub|open-cluster-management-addon.+"})/(1024*1024*1024)')

        acm_cpu_df = MetricSnapshotDataFrame(acm_cpu)
        acm_cpu_df["value"]=acm_cpu_df["value"].astype(float)
        acm_cpu_df.rename(columns={"value": "ACMOthMemUsageWSSGB"}, inplace = True)
        print(acm_cpu_df[['ACMOthMemUsageWSSGB']].to_markdown())

        acm_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace=~"multicluster-engine|open-cluster-management-agent.+|open-cluster-management-hub|open-cluster-management-addon.+"})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_cpu_trend_df = MetricRangeDataFrame(acm_cpu_trend)
        acm_cpu_trend_df["value"]=acm_cpu_trend_df["value"].astype(float)
        acm_cpu_trend_df.index= pandas.to_datetime(acm_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        acm_cpu_trend_df.rename(columns={"value": "ACMOthMemUsageWSSGB"}, inplace = True)
        acm_cpu_trend_df.plot(title="ACM Other Memory (wss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/acm-oth-mem-usage-wss.png')
        saveCSV(acm_cpu_trend_df,"acm-oth-mem-usage-wss",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting Memory (wss) for ACM Others: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def ACMObsDetailMemUsageRSS(pc,startTime, endTime, step):

    print("Detailed ACM Obs Memory (rss) usage GB")

    try:
        acm_detail_cpu = pc.custom_query('(sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace="open-cluster-management-observability"}) by (container))/(1024*1024*1024)')

        acm_detail_cpu_df = MetricSnapshotDataFrame(acm_detail_cpu)
        acm_detail_cpu_df["value"]=acm_detail_cpu_df["value"].astype(float)
        acm_detail_cpu_df.rename(columns={"value": "ACMObsDetailMemUsageRSSGB"}, inplace = True)
        print(acm_detail_cpu_df[['container','ACMObsDetailMemUsageRSSGB']].to_markdown())

        acm_detail_cpu_trend = pc.custom_query_range(
        query='(sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace="open-cluster-management-observability"}) by (container))/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_detail_cpu_trend_df = MetricRangeDataFrame(acm_detail_cpu_trend)
        acm_detail_cpu_trend_df["value"]=acm_detail_cpu_trend_df["value"].astype(float)
        acm_detail_cpu_trend_df.index= pandas.to_datetime(acm_detail_cpu_trend_df.index, unit="s")
        acm_detail_cpu_trend_df =  acm_detail_cpu_trend_df.pivot( columns='container',values='value')
        acm_detail_cpu_trend_df.plot(title="ACM Obs Detailed Memory (rss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/breakdown/acm-obs-detail-mem-usage-rss.png')
        saveCSV(acm_detail_cpu_trend_df,"acm-obs-detail-mem-usage-rss")
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting memory (rss) details for ACM Obs: ",e)    
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status

def ACMObsDetailMemUsageWSS(pc,startTime, endTime, step):

    print("Detailed ACM Obs Memory (wss) usage GB")

    try:
        acm_detail_cpu = pc.custom_query('(sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace="open-cluster-management-observability"}) by (container))/(1024*1024*1024)')

        acm_detail_cpu_df = MetricSnapshotDataFrame(acm_detail_cpu)
        acm_detail_cpu_df["value"]=acm_detail_cpu_df["value"].astype(float)
        acm_detail_cpu_df.rename(columns={"value": "ACMObsDetailMemUsageWSSGB"}, inplace = True)
        print(acm_detail_cpu_df[['container','ACMObsDetailMemUsageWSSGB']].to_markdown())

        acm_detail_cpu_trend = pc.custom_query_range(
        query='(sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace="open-cluster-management-observability"}) by (container))/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_detail_cpu_trend_df = MetricRangeDataFrame(acm_detail_cpu_trend)
        acm_detail_cpu_trend_df["value"]=acm_detail_cpu_trend_df["value"].astype(float)
        acm_detail_cpu_trend_df.index= pandas.to_datetime(acm_detail_cpu_trend_df.index, unit="s")
        acm_detail_cpu_trend_df =  acm_detail_cpu_trend_df.pivot( columns='container',values='value')
        acm_detail_cpu_trend_df.plot(title="ACM Obs Detailed Memory (wss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/breakdown/acm-obs-detail-mem-usage-wss.png')
        saveCSV(acm_detail_cpu_trend_df,"acm-obs-detail-mem-usage-wss")
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting memory (wss) details for ACM Obs: ",e)    
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status

def ACMObsRecvMemUsageRSS(pc,startTime, endTime, step):

    print("Total ACM ObsRecv Memory (rss) usage GB")

    try:
        acm_cpu = pc.custom_query('sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container="thanos-receive", namespace="open-cluster-management-observability"})/(1024*1024*1024)')

        acm_cpu_df = MetricSnapshotDataFrame(acm_cpu)
        acm_cpu_df["value"]=acm_cpu_df["value"].astype(float)
        acm_cpu_df.rename(columns={"value": "ACMObsRecvMemUsageRSSGB"}, inplace = True)
        print(acm_cpu_df[['ACMObsRecvMemUsageRSSGB']].to_markdown())

        acm_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container="thanos-receive", namespace="open-cluster-management-observability"})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_cpu_trend_df = MetricRangeDataFrame(acm_cpu_trend)
        acm_cpu_trend_df["value"]=acm_cpu_trend_df["value"].astype(float)
        acm_cpu_trend_df.index= pandas.to_datetime(acm_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        acm_cpu_trend_df.rename(columns={"value": "ACMObsRecvMemUsageRSSGB"}, inplace = True)
        acm_cpu_trend_df.plot(title="ACM ObsRecv Memory (rss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/acm-obs-recv-mem-usage-rss.png')
        saveCSV(acm_cpu_trend_df,"acm-obs-recv-mem-usage-rss",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting Memory (rss) for ACM ObsRecv: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def ACMObsRecvMemUsageWSS(pc,startTime, endTime, step):

    print("Total ACM ObsRecv Memory (wss) usage GB")

    try:
        acm_cpu = pc.custom_query('sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container="thanos-receive", image!="",namespace="open-cluster-management-observability"})/(1024*1024*1024)')

        acm_cpu_df = MetricSnapshotDataFrame(acm_cpu)
        acm_cpu_df["value"]=acm_cpu_df["value"].astype(float)
        acm_cpu_df.rename(columns={"value": "ACMObsRecvMemUsageWSSGB"}, inplace = True)
        print(acm_cpu_df[['ACMObsRecvMemUsageWSSGB']].to_markdown())

        acm_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container="thanos-receive", image!="",namespace="open-cluster-management-observability"})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_cpu_trend_df = MetricRangeDataFrame(acm_cpu_trend)
        acm_cpu_trend_df["value"]=acm_cpu_trend_df["value"].astype(float)
        acm_cpu_trend_df.index= pandas.to_datetime(acm_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        acm_cpu_trend_df.rename(columns={"value": "ACMObsRecvMemUsageWSSGB"}, inplace = True)
        acm_cpu_trend_df.plot(title="ACM ObsRecv Memory (wss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/acm-obs-recv-mem-usage-wss.png')
        saveCSV(acm_cpu_trend_df,"acm-obs-recv-mem-usage-wss",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting Memory (wss) for ACM ObsRecv: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def ACMOCMDetailMemUsageRSS(pc,startTime, endTime, step):

    print("Detailed ACM Open cluster management Memory (rss) usage GB")

    try:
        acm_detail_cpu = pc.custom_query('(sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace="open-cluster-management"}) by (container))/(1024*1024*1024)')

        acm_detail_cpu_df = MetricSnapshotDataFrame(acm_detail_cpu)
        acm_detail_cpu_df["value"]=acm_detail_cpu_df["value"].astype(float)
        acm_detail_cpu_df.rename(columns={"value": "ACMOCMDetailMemUsageRSSGB"}, inplace = True)
        print(acm_detail_cpu_df[['container','ACMOCMDetailMemUsageRSSGB']].to_markdown())

        acm_detail_cpu_trend = pc.custom_query_range(
        query='(sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", namespace="open-cluster-management"}) by (container))/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_detail_cpu_trend_df = MetricRangeDataFrame(acm_detail_cpu_trend)
        acm_detail_cpu_trend_df["value"]=acm_detail_cpu_trend_df["value"].astype(float)
        acm_detail_cpu_trend_df.index= pandas.to_datetime(acm_detail_cpu_trend_df.index, unit="s")
        acm_detail_cpu_trend_df =  acm_detail_cpu_trend_df.pivot( columns='container',values='value')
        acm_detail_cpu_trend_df.plot(title="ACM Open cluster management Detailed Memory (rss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/breakdown/acm-ocm-detail-mem-usage-rss.png')
        saveCSV(acm_detail_cpu_trend_df,"acm-ocm-detail-mem-usage-rss")
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting memory (rss) details for ACM Open cluster management: ",e)    
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status

def ACMOCMDetailMemUsageWSS(pc,startTime, endTime, step):

    print("Detailed ACM Open cluster management Memory (wss) usage GB")

    try:
        acm_detail_cpu = pc.custom_query('(sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace="open-cluster-management"}) by (container))/(1024*1024*1024)')

        acm_detail_cpu_df = MetricSnapshotDataFrame(acm_detail_cpu)
        acm_detail_cpu_df["value"]=acm_detail_cpu_df["value"].astype(float)
        acm_detail_cpu_df.rename(columns={"value": "ACMOCMDetailMemUsageWSSGB"}, inplace = True)
        print(acm_detail_cpu_df[['container','ACMOCMDetailMemUsageWSSGB']].to_markdown())

        acm_detail_cpu_trend = pc.custom_query_range(
        query='(sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container!="", image!="",namespace="open-cluster-management"}) by (container))/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_detail_cpu_trend_df = MetricRangeDataFrame(acm_detail_cpu_trend)
        acm_detail_cpu_trend_df["value"]=acm_detail_cpu_trend_df["value"].astype(float)
        acm_detail_cpu_trend_df.index= pandas.to_datetime(acm_detail_cpu_trend_df.index, unit="s")
        acm_detail_cpu_trend_df =  acm_detail_cpu_trend_df.pivot( columns='container',values='value')
        acm_detail_cpu_trend_df.plot(title="ACM Open cluster management Detailed Memory (wss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/breakdown/acm-ocm-detail-mem-usage-wss.png')
        saveCSV(acm_detail_cpu_trend_df,"acm-ocm-detail-mem-usage-wss")
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting memory (wss) details for ACM Open cluster management: ",e)    
        print(Style.RESET_ALL)
    print("=============================================")
   
    status=True
    return status

def ACMSrcPGvMemUsageRSS(pc,startTime, endTime, step):

    print("Total ACM Search Postgres Memory (rss) usage GB")

    try:
        acm_cpu = pc.custom_query('sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container="search-postgres", namespace="open-cluster-management"})/(1024*1024*1024)')

        acm_cpu_df = MetricSnapshotDataFrame(acm_cpu)
        acm_cpu_df["value"]=acm_cpu_df["value"].astype(float)
        acm_cpu_df.rename(columns={"value": "ACMSearchPGMemUsageRSSGB"}, inplace = True)
        print(acm_cpu_df[['ACMSearchPGMemUsageRSSGB']].to_markdown())

        acm_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container="search-postgres", namespace="open-cluster-management"})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_cpu_trend_df = MetricRangeDataFrame(acm_cpu_trend)
        acm_cpu_trend_df["value"]=acm_cpu_trend_df["value"].astype(float)
        acm_cpu_trend_df.index= pandas.to_datetime(acm_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        acm_cpu_trend_df.rename(columns={"value": "ACMSearchPGMemUsageRSSGB"}, inplace = True)
        acm_cpu_trend_df.plot(title="ACM Search Postgres Memory (rss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/acm-src-pg-mem-usage-rss.png')
        saveCSV(acm_cpu_trend_df,"acm-src-pg-mem-usage-rss",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting Memory (rss) for ACM Search Postgres: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def ACMOSrcPGMemUsageWSS(pc,startTime, endTime, step):

    print("Total ACM Search Postgres Memory (wss) usage GB")

    try:
        acm_cpu = pc.custom_query('sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container="search-postgres", image!="",namespace="open-cluster-management"})/(1024*1024*1024)')

        acm_cpu_df = MetricSnapshotDataFrame(acm_cpu)
        acm_cpu_df["value"]=acm_cpu_df["value"].astype(float)
        acm_cpu_df.rename(columns={"value": "ACMSearchPGMemUsageWSSGB"}, inplace = True)
        print(acm_cpu_df[['ACMSearchPGMemUsageWSSGB']].to_markdown())

        acm_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container="search-postgres", image!="",namespace="open-cluster-management"})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_cpu_trend_df = MetricRangeDataFrame(acm_cpu_trend)
        acm_cpu_trend_df["value"]=acm_cpu_trend_df["value"].astype(float)
        acm_cpu_trend_df.index= pandas.to_datetime(acm_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        acm_cpu_trend_df.rename(columns={"value": "ACMSearchPGMemUsageWSSGB"}, inplace = True)
        acm_cpu_trend_df.plot(title="ACM Search Postgres Memory (wss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/acm-src-pg-mem-usage-wss.png')
        saveCSV(acm_cpu_trend_df,"acm-src-pg-mem-usage-wss",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting Memory (wss) for ACM Search Postgres: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def ACMSrcIdxvMemUsageRSS(pc,startTime, endTime, step):

    print("Total ACM Search Indexer Memory (rss) usage GB")

    try:
        acm_cpu = pc.custom_query('sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container="search-indexer", namespace="open-cluster-management"})/(1024*1024*1024)')

        acm_cpu_df = MetricSnapshotDataFrame(acm_cpu)
        acm_cpu_df["value"]=acm_cpu_df["value"].astype(float)
        acm_cpu_df.rename(columns={"value": "ACMSearchIdxMemUsageRSSGB"}, inplace = True)
        print(acm_cpu_df[['ACMSearchIdxMemUsageRSSGB']].to_markdown())

        acm_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_rss{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container="search-indexer", namespace="open-cluster-management"})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_cpu_trend_df = MetricRangeDataFrame(acm_cpu_trend)
        acm_cpu_trend_df["value"]=acm_cpu_trend_df["value"].astype(float)
        acm_cpu_trend_df.index= pandas.to_datetime(acm_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        acm_cpu_trend_df.rename(columns={"value": "ACMSearchIdxMemUsageRSSGB"}, inplace = True)
        acm_cpu_trend_df.plot(title="ACM Search Indexer Memory (rss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/acm-src-idx-mem-usage-rss.png')
        saveCSV(acm_cpu_trend_df,"acm-src-idx-mem-usage-rss",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting Memory (rss) for ACM Search Indexer: ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status

def ACMOSrcIdxMemUsageWSS(pc,startTime, endTime, step):

    print("Total ACM Search Indexer Memory (wss) usage GB")

    try:
        acm_cpu = pc.custom_query('sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container="search-indexer", image!="",namespace="open-cluster-management"})/(1024*1024*1024)')

        acm_cpu_df = MetricSnapshotDataFrame(acm_cpu)
        acm_cpu_df["value"]=acm_cpu_df["value"].astype(float)
        acm_cpu_df.rename(columns={"value": "ACMSearchIdxMemUsageWSSGB"}, inplace = True)
        print(acm_cpu_df[['ACMSearchIdxMemUsageWSSGB']].to_markdown())

        acm_cpu_trend = pc.custom_query_range(
        query='sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", container="search-indexer", image!="",namespace="open-cluster-management"})/(1024*1024*1024)',
            start_time=startTime,
            end_time=endTime,
            step=step,
        )

        acm_cpu_trend_df = MetricRangeDataFrame(acm_cpu_trend)
        acm_cpu_trend_df["value"]=acm_cpu_trend_df["value"].astype(float)
        acm_cpu_trend_df.index= pandas.to_datetime(acm_cpu_trend_df.index, unit="s")
        #node_cpu_trend_df =  node_cpu_trend_df.pivot( columns='node',values='value')
        acm_cpu_trend_df.rename(columns={"value": "ACMSearchIdxMemUsageWSSGB"}, inplace = True)
        acm_cpu_trend_df.plot(title="ACM Search Indexer  Memory (wss) usage GB",figsize=(30, 15))
        plt.savefig('../../output/acm-src-idx-mem-usage-wss.png')
        saveCSV(acm_cpu_trend_df,"acm-src-idx-mem-usage-wss",True)
        plt.close('all')

    except Exception as e:
        print(Fore.RED+"Error in getting Memory (wss) for ACM Search Indexer : ",e)  
        print(Style.RESET_ALL)  
    print("=============================================")
   
    status=True
    return status