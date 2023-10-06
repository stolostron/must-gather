from kubernetes import client, config
from colorama import Fore, Back, Style
import sys

import numpy as np
from utility import *

import pandas

def checkNodeStatus(debug=False):
    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print("Node Health Check")
    print("************************************************************************************************")
    print(Style.RESET_ALL)
    status = True
    

    

    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()

    v1 = client.CoreV1Api()
    # print("Listing pods with their IPs:")
    # ret = v1.list_pod_for_all_namespaces(watch=False)
    # for i in ret.items:
    #     print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

    try:
        nodes=v1.list_node(_request_timeout=1) 
        nodeDetailsList=[] 
        node_df = pandas.DataFrame()
        for node in nodes.items:
            nodeDetails={}
            #print("----")
            #print(node.metadata.name)
            #print(node.spec)

            nodeDetails['name']=node.metadata.name
            #nodeList['spec']=node.spec
            #print(node.status.conditions)

            #print(node.status.capacity)
            for k,v in  node.status.capacity.items():
                if k.startswith("cpu") or k.startswith("memory") :
                    nodeDetails[k]=v

            #print(node.metadata.labels)
            rolevalue=''
            for x in  node.metadata.labels:
                if x.startswith("node-role.kubernetes.io") : 
                    rolevalue=rolevalue+", "+x.removeprefix("node-role.kubernetes.io/")
                    #print(x.removeprefix("node-role.kubernetes.io/"))
                    
            nodeDetails['role']=rolevalue

            for mc in node.status.conditions:
                #print(mc)
                #print(mc.type,"::",mc.status )
                nodeDetails[mc.type]=mc.status
            if debug: nodeDetails['spec']=node.spec
            #print(nodeDetails) 
            nodeDetailsList.append(nodeDetails)
        
        node_df = pandas.DataFrame.from_records(nodeDetailsList)  
        print(node_df.to_markdown()) 
        node_df["Ready"]=node_df["Ready"].astype(bool)
        
        if False in node_df["Ready"].values :
            print("Problematic Nodes")
            print(node_df[node_df["Ready"] == False])
            status= False

        saveCSV( node_df, "node-list")


        #Summarizing Node details to send to Utility module
        
        #Lets fix the CPU data type to int
        node_df["cpu"]=node_df["cpu"].astype(int)

        node_df["memory_unit"]=node_df["memory"].str[-2:]
        node_df["memory_revised"]=node_df["memory"].str[:-2].astype(float)

        #Convert KiB to GiB (thats what Prom does) and MiB to GiB
        node_df["memory_gib"] = np.where( node_df["memory_unit"] == 'Ki' , node_df["memory_revised"]/1.049e+6 , node_df["memory_revised"]/1024 )

        ncount = node_df.shape[0]
        n_master_df = node_df[node_df["role"].str.contains('master')]
        ncount_master=n_master_df.shape[0]
        n_worker_df = node_df[node_df["role"].str.contains('worker')]
        ncount_worker=n_worker_df.shape[0]
        if ncount >3 : 
            n_compact = False
        else:
            n_compact = True   
      
        nmaster_cpu_core=n_master_df["cpu"].sum(axis = 0, skipna = True)
        nworker_cpu_core=n_worker_df["cpu"].sum(axis = 0, skipna = True)

        nmaster_memory_gib=n_master_df["memory_gib"].sum(axis = 0, skipna = True)
        nworker_memory_gib=n_worker_df["memory_gib"].sum(axis = 0, skipna = True)

        print("-------------------------------------------------------")
        print("Quick Node Analysis....:")
        print("Count of nodes....",ncount)
        print("Count of master nodes....",ncount_master)
        print("Count of worker nodes....",ncount_worker)
        print("Is this a compact cluster with schedulable masters....",n_compact)
        print("Master Node CPU VCore count....",nmaster_cpu_core)
        print("Worker Node CPU VCore count....",nworker_cpu_core)
        print("Master Node Memory GiB....",nmaster_memory_gib)
        print("Worker Node Memory GiB....",nworker_memory_gib)

        print("-------------------------------------------------------")

        nodeDetails={}
        nodeDetails['numNodes']=ncount
        nodeDetails['numMasterNodes']=ncount_master
        nodeDetails['numWorkerNodes']=ncount_worker
        nodeDetails['compact']=n_compact
        nodeDetails['sumCPUVCoreMaster']=nmaster_cpu_core
        nodeDetails['sumCPUVCoreWorker']=nworker_cpu_core
        nodeDetails['sumMemoryGiBMaster']=nmaster_memory_gib
        nodeDetails['sumMemoryGiBWorker']=nworker_memory_gib

        # Setting Node details in Utility module
        setNodeDetails(nodeDetails)

        print(Back.LIGHTYELLOW_EX+"")
        print("************************************************************************************************")
        print(" Node Health Check passed ============ ", status)
        print("************************************************************************************************")
        print(Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED+"Failure: ",e)
        sys.exit("Cluster may be down, or credentials may be wrong, or simply not connected")
        print(Style.RESET_ALL)
    return status

