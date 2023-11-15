import os
from prometheus_api_client import *
from kubernetes import client, config
import sys
import datetime
import pandas
from colorama import Fore, Back, Style
import matplotlib.pyplot as plt
import os

# To be able to start the dataframe merge, we need this global variable
initialDF = pandas.DataFrame()
masterDF = pandas.DataFrame()
nodeDetails={}


def setNodeDetails(details) :
    
    nodeDetails['numNodes']=details['numNodes']
    nodeDetails['numMasterNodes']=details['numMasterNodes']
    nodeDetails['numWorkerNodes']=details['numWorkerNodes']
    nodeDetails['compact']=details['compact']
    nodeDetails['sumCPUVCoreMaster']=details['sumCPUVCoreMaster']
    nodeDetails['sumCPUVCoreWorker']=details['sumCPUVCoreWorker']
    nodeDetails['sumMemoryGiBMaster']=details['sumMemoryGiBMaster']
    nodeDetails['sumMemoryGiBWorker']=details['sumMemoryGiBWorker']


def createSubdir() :

    global inspector_dir
    try:
        inspector_dir = os.getenv('BASE_COLLECTION_PATH') + "/acm-inspector/"
    except TypeError:
        inspector_dir = "/must-gather/acm-inspector/"

    # Specify the directory name you want to create
    subdir_name = "breakdown"

    # Construct the full path to the subdirectory
    subdir_path = os.path.join(inspector_dir,subdir_name)

    try:
        os.makedirs(subdir_path)
    except Exception as e:
        print(Fore.RED+"Breakdown subdir probably exists: ",e)  
        print(Style.RESET_ALL)    

    print(f"Subdirectory '{subdir_name}' created in '{subdir_path}'.")


def promConnect():

    tsdb = sys.argv[1]
    #print(f"Arguments of the script : ", tsdb)

    try:
        if tsdb == "prom" :
            # Get the Prometheus URL from the Route object.
            custom_object_api = client.CustomObjectsApi()
            promRoute = custom_object_api.get_namespaced_custom_object(
                "route.openshift.io", "v1", "openshift-monitoring", "routes", "thanos-querier")
            prom_url = "https://{}".format(promRoute['spec']['host'])
            #print("Connecting to ACM Hub at URL: ",prom_url)
        else:
            # Get the Prometheus URL from the Route object.
            custom_object_api = client.CustomObjectsApi()
            promRoute = custom_object_api.get_namespaced_custom_object(
                "route.openshift.io", "v1", "open-cluster-management-observability", "routes", "rbac-query-proxy")
            #if using observability, use below
            prom_url = "https://{}/".format(promRoute['spec']['host'])
            #print("Connecting to ACM Hub at URL: ",prom_url)    

        # Get Kubernetes API token.
        c = client.Configuration()
        config.load_config(client_configuration = c)
        api_token = c.api_key['authorization']
        #for k,v in c.api_key.items():
        #    print(k,v)

        #connects to prometheus
        pc = PrometheusConnect(url=prom_url, headers={"Authorization": "{}".format(api_token)}, disable_ssl=True)
    
    except Exception as e:
        print("Failure: ",e) 
        sys.exit("Is PROM_URL, API_TOKEN env variables defined or are they accurate")       
    
    return pc

def helperTime():
    start_time=(datetime.datetime.now() - datetime.timedelta(minutes=2880))
    end_time=datetime.datetime.now()
    step='1m'
    return start_time, end_time,step  

def saveCSV(df, filename, merge = False):
    try:
        if merge == True:
            global masterDF
            df.to_csv(inspector_dir + '/'+filename+'.csv', index = True, header=True)

            if masterDF.empty:
                #masterDF = pandas.merge(initialDF, df, how ='inner', on ='timestamp')
                masterDF = initialDF
                # print("-----------------------------------")
                # print(initialDF)
                # print("-----------------------------------")
                # print(df)
                # print("-----------------------------------")
                # print(masterDF)
                # print("-----------------------------------")
            else:
                masterDF=pandas.merge(masterDF, df, how ='inner', on ='timestamp')
            #print(masterDF)
        else:
            df.to_csv(inspector_dir + '/breakdown/'+filename+'.csv', index = True, header=True)
    except Exception as e:
        print(Fore.RED+"Failure in saving to CSV: ",e) 
        print(Style.RESET_ALL)    

def setInitialDF(df): 
    global initialDF
    try:
        initialDF = df
    except Exception as e:
        print("Failure in setting masterDF: ",e)

    print("MasterDF set..")
    print(initialDF)


def saveMasterDF(): 
    try:
        masterDF.to_csv(inspector_dir + '/master.csv', index = True, header=True)  
        print("MasterDF saved..")
    except Exception as e:
        print(Fore.RED+"Failure in saving masterDF: ",e)  
        print(Style.RESET_ALL)  
    
    print("Now creating the master graphs....")
    plotCPU(nodeDetails["compact"])  
    plotMemory(nodeDetails["compact"])
    plotAPIEtcdSizing(nodeDetails["compact"])
    plotAPIEtcdTiming(nodeDetails["compact"])
    plotAPIServerResources(nodeDetails["compact"])
    plotACMResources(nodeDetails["compact"])
    plotMasterThanos(nodeDetails["compact"])

def cleanList(inputList):
    common_elements = [element for element in inputList if element in masterDF.columns.tolist()]
    return common_elements


def plotCPU(isCompactCluster):
    try:
        if isCompactCluster:

            fig, ax = plt.subplots(figsize=(30,15)) 


            y1array=cleanList(["ClusterCPUCoreUsage","ClusterCPUCoreCap","KubeAPICPUCoreUsage","ACMCPUCoreUsage",
                     "OtherCPUCoreUsage","ACMObsCPUCoreUsage","ACMOthCPUCoreUsage","ACMObsRecvCPUCoreUsage"])

            masterDF.plot(y=["ManagedClusterCount"], ax = ax) 
            masterDF.plot(y=y1array, ax = ax, secondary_y = True)
            plt.title("Combined Master CPU chart")
            plt.savefig(inspector_dir + '/master-cpu.png')

        # if it non-3 node cluster - we do need to separately deal with
        # Master Node capacity and Worker Nodes capacity
        else :
            fig, ax = plt.subplots(figsize=(30,15)) 
  

            y1array =cleanList(["ClusterCPUCoreUsage","ClusterCPUCoreCap","KubeAPICPUCoreUsage","ACMCPUCoreUsage",
                       "OtherCPUCoreUsage","ACMObsCPUCoreUsage","ACMOthCPUCoreUsage","ACMObsRecvCPUCoreUsage"])

            masterDF.plot(y=["ManagedClusterCount"], ax = ax) 
            masterDF.plot(y=y1array, ax = ax, secondary_y = True)
            
            plt.axhline(y = nodeDetails["sumCPUVCoreMaster"], linestyle = 'dashed', label = "Master Node Capacity") 
            plt.axhline(y = nodeDetails["sumCPUVCoreWorker"], linestyle = 'dashed', label = "Worker Node Capacity")
            #plt.legend()
            plt.title("Combined Master CPU chart")
            plt.savefig(inspector_dir + '/master-cpu.png')
        
            # masterDF.plot(y=["ManagedClusterCount", "KubeAPICPUCoreUsage"],
            #             title="Combined Master Master Node CPU chart", kind="line", figsize=(30, 15))
            
            fig, ax = plt.subplots(figsize=(30,15))
            masterDF.plot(y=["ManagedClusterCount"], ax = ax) 
            masterDF.plot(y=["KubeAPICPUCoreUsage"], ax = ax, secondary_y = True)            
            
            plt.axhline(y = nodeDetails["sumCPUVCoreMaster"], linestyle = 'dashed', label = "Master Node Capacity") 
            #plt.legend()
            plt.title("Combined Master Master Node CPU chart")
            plt.savefig(inspector_dir + '/master-cpu-masternode.png')

            # masterDF.plot(y=["ManagedClusterCount", "ACMCPUCoreUsage"],
            #             title="Combined Master Worker Node CPU chart", kind="line", figsize=(30, 15))
            
            y2array=cleanList(["ACMCPUCoreUsage","ACMObsCPUCoreUsage","ACMOthCPUCoreUsage","ACMObsRecvCPUCoreUsage"])
            fig, ax = plt.subplots(figsize=(30,15))
            masterDF.plot(y=["ManagedClusterCount"], ax = ax) 
            masterDF.plot(y=y2array, ax = ax, secondary_y = True) 
            
            plt.axhline(y = nodeDetails["sumCPUVCoreWorker"], linestyle = 'dashed', label = "Worker Node Capacity") 
            #plt.legend()
            plt.title("Combined Master Worker Node CPU chart")
            plt.savefig(inspector_dir + '/master-cpu-workernode.png')            
    except Exception as e:
        print(Fore.RED+"Failure in drawing graph Combined Master CPU chart - probably metrics are missing: ",e)  
        print(Style.RESET_ALL)

def plotMemory(isCompactCluster) :
    try :
        if isCompactCluster:      
            # masterDF.plot(y=["ManagedClusterCount", "ClusterMemUsageGB","ClusterMemCapacityGB","KubeAPIMemUsageGB","ACMMemUsageGB"],
            #             title="Combined Master Master Node Memory chart", kind="line", figsize=(30, 15))
            fig, ax = plt.subplots(figsize=(30,15)) 

            y1array=cleanList(["ClusterMemUsageGB","ClusterMemCapacityGB","KubeAPIMemUsageRSSGB","ACMMemUsageRSSGB",
                     "OtherMemUsageRSSGB","ACMOthMemUsageRSSGB","ACMObsMemUsageRSSGB","KubeAPIMemUsageWSSGB",
                     "ACMMemUsageWSSGB","OtherMemUsageWSSGB","ACMOthMemUsageWSSGB","ACMObsMemUsageWSSGB"])
            masterDF.plot(y=["ManagedClusterCount"], ax = ax) 
            masterDF.plot(y=y1array, ax = ax, secondary_y = True)
            plt.title("Combined Master Master Node Memory chart")
            plt.savefig(inspector_dir + '/master-memory.png')
        
        # if it non-3 node cluster - we do need to separately deal with
        # Master Node capacity and Worker Nodes capacity
        else :
            # masterDF.plot(y=["ManagedClusterCount", "ClusterMemUsageGB","ClusterMemCapacityGB","KubeAPIMemUsageGB","ACMMemUsageGB"],
            #             title="Combined Master Master Node Memory chart", kind="line", figsize=(30, 15))
            fig, ax = plt.subplots(figsize=(30,15))
            
            y1array=cleanList(["ClusterMemUsageGB","ClusterMemCapacityGB","KubeAPIMemUsageRSSGB","ACMMemUsageRSSGB",
                     "OtherMemUsageRSSGB","ACMOthMemUsageRSSGB","ACMObsMemUsageRSSGB","KubeAPIMemUsageWSSGB",
                     "ACMMemUsageWSSGB","OtherMemUsageWSSGB","ACMOthMemUsageWSSGB","ACMObsMemUsageWSSGB"])
            masterDF.plot(y=["ManagedClusterCount"], ax = ax) 
            masterDF.plot(y=y1array, ax = ax, secondary_y = True) 

            plt.axhline(y = nodeDetails["sumMemoryGiBMaster"], linestyle = 'dashed', label = "Master Node Capacity") 
            plt.axhline(y = nodeDetails["sumMemoryGiBWorker"], linestyle = 'dashed', label = "Worker Node Capacity") 
            #plt.legend()
            plt.title("Combined Master Master Node Memory chart")
            plt.savefig(inspector_dir + '/master-memory.png')
        
            # masterDF.plot(y=["ManagedClusterCount", "KubeAPIMemUsageGB"],
            #             title="Combined Master Worker Node Memory chart", kind="line", figsize=(30, 15))
            fig, ax = plt.subplots(figsize=(30,15))
            masterDF.plot(y=["ManagedClusterCount"], ax = ax) 
            masterDF.plot(y=["KubeAPIMemUsageRSSGB","KubeAPIMemUsageWSSGB"], ax = ax, secondary_y = True)             
            plt.axhline(y = nodeDetails["sumMemoryGiBMaster"], linestyle = 'dashed', label = "Master Node Capacity") 
            #plt.legend()
            plt.title("Combined Master Worker Node Memory chart")
            plt.savefig(inspector_dir + '/master-memory-masternode.png')

            # masterDF.plot(y=["ManagedClusterCount","ACMMemUsageGB"],
            #             title="Combined Master Memory chart", kind="line", figsize=(30, 15))
            fig, ax = plt.subplots(figsize=(30,15))

            y2array=cleanList(["ACMMemUsageRSSGB","OtherMemUsageRSSGB","ACMOthMemUsageRSSGB","ACMObsMemUsageRSSGB",
                     "ACMMemUsageWSSGB","OtherMemUsageWSSGB","ACMOthMemUsageWSSGB","ACMObsMemUsageWSSGB"])
            masterDF.plot(y=["ManagedClusterCount"], ax = ax) 
            masterDF.plot(y=y2array, ax = ax, secondary_y = True)             
            plt.axhline(y = nodeDetails["sumMemoryGiBWorker"], linestyle = 'dashed', label = "Worker Node Capacity") 
            #plt.legend()
            plt.title("Combined Master Memory chart")
            plt.savefig(inspector_dir + '/master-memory-workernode.png')
    except Exception as e:
        print(Fore.RED+"Failure in drawing graph Combined Master Memory chart - probably metrics are missing: ",e)  
        print(Style.RESET_ALL)

def plotAPIEtcdSizing(isCompactCluster) :        
    try:            
        fig, ax = plt.subplots(figsize=(30,15))  

        masterDF.plot(y=["ManagedClusterCount"], ax = ax) 
        masterDF.plot(y=["etcdDBLeaderElection","etcdDBSizeUsedMB","etcdDBSizeMB"], ax = ax, secondary_y = True) 
        plt.title("Combined Master API-ETCD chart") 
        plt.savefig(inspector_dir + '/master-api-etcd.png')
    except Exception as e:
        print(Fore.RED+"Failure in drawing graph Combined Master API-ETCD chart - probably metrics are missing: ",e)  
        print(Style.RESET_ALL)  

def plotAPIEtcdTiming(isCompactCluster) :   
    try:            

        fig, ax = plt.subplots(figsize=(30,15))  

        masterDF.plot(y=["ManagedClusterCount"], ax = ax) 
        masterDF.plot(y=["etcdBackendCommitDuration","etcdWalSyncDuration","etcdNetWorkPeerRoundTripDuration","etcdCPUIOWaitDuration"], ax = ax, secondary_y = True) 
        plt.title("Combined Master ETCD Timing chart") 
        plt.savefig(inspector_dir + '/master-etcd-timing.png')
    except Exception as e:
        print(Fore.RED+"Failure in drawing graph Combined Master API-ETCD chart - probably metrics are missing: ",e)  
        print(Style.RESET_ALL)   

def plotMasterThanos(isCompactCluster) :
    try:    
        #this will not work if Obs. is not installed. So we will need special processing
        # masterDF.plot(y=["ManagedClusterCount", "CompactorHalted","recvsync90","recvsync95","recvsync99"],
        #              title="Combined Master Thanos chart", kind="line", figsize=(30, 15))
        
        fig, ax = plt.subplots(figsize=(30,15)) 

        masterDF.plot(y=["ManagedClusterCount"], ax = ax) 
        masterDF.plot(y=["CompactorHalted","recvsync90","recvsync95","recvsync99"], ax = ax, secondary_y = True) 
        plt.title("Combined Master Thanos chart")
        plt.savefig(inspector_dir + '/master-thanos.png')
    except Exception as e:
        print(Fore.RED+"Failure in drawing graph Combined Master Thanos chart - probably ACM Obs is not installed: ",e)  
        print(Style.RESET_ALL) 

def plotACMResources(isCompactCluster) :
    try:    
        # masterDF.plot(y=["ManagedClusterCount", 'APIServerconfigurationpolicies.policy.open-cluster-management.ioCount',
        #                  'APIServermanifestworks.work.open-cluster-management.ioCount','APIServerplacements.cluster.open-cluster-management.ioCount',
        #                  'APIServersubscriptions.apps.open-cluster-management.ioCount','APIServerapplications.app.k8s.ioCount',
        #                  'APIServerapplications.argoproj.ioCount','APIServerapplicationsets.argoproj.ioCount'],
        #               title="Combined ACM Resources", kind="line", figsize=(30, 15))
        
        fig, ax = plt.subplots(figsize=(30,15)) 

        y1array=cleanList(['APIServerconfigurationpolicies.policy.open-cluster-management.ioCount',
                        'APIServermanifestworks.work.open-cluster-management.ioCount','APIServerplacements.cluster.open-cluster-management.ioCount',
                        'APIServersubscriptions.apps.open-cluster-management.ioCount','APIServerapplications.app.k8s.ioCount',
                        'APIServerapplications.argoproj.ioCount','APIServerapplicationsets.argoproj.ioCount'])

        masterDF.plot(y=["ManagedClusterCount"], ax = ax) 
        masterDF.plot(y=y1array, ax = ax, secondary_y = True)
        plt.title("Combined ACM Resources")
        plt.savefig(inspector_dir + '/master-ACMResources.png')
    except Exception as e:
        print(Fore.RED+"Failure in drawing graph Combined ACM Resources - probably metrics are missing: ",e)  
        print(Style.RESET_ALL)  

def plotAPIServerResources(isCompactCluster):
    try:
        # the column names can be derived dynamically from the dataframe or apiServerObjects.py module
        # masterDF.plot(y=["ManagedClusterCount", "APIServersecretsCount","APIServerconfigmapsCount","APIServerserviceaccountsCount",
        #                  'APIServerclusterrolebindings.rbac.authorization.k8s.ioCount','APIServerrolebindings.rbac.authorization.k8s.ioCount',
        #                  'APIServerclusterroles.rbac.authorization.k8s.ioCount','APIServerroles.rbac.authorization.k8s.ioCount',
        #                  'APIServerleases.coordination.k8s.ioCount','APIServerconfigurationpolicies.policy.open-cluster-management.ioCount',
        #                  'APIServermanifestworks.work.open-cluster-management.ioCount','APIServerplacements.cluster.open-cluster-management.ioCount',
        #                  'APIServersubscriptions.apps.open-cluster-management.ioCount','APIServerapplications.app.k8s.ioCount',
        #                  'APIServerapplications.argoproj.ioCount','APIServerapplicationsets.argoproj.ioCount'],
        #               title="Combined Master API Server Object Count", kind="line", figsize=(30, 15))
        
        fig, ax = plt.subplots(figsize=(30,15)) 

        y1array=cleanList(["APIServersecretsCount","APIServerconfigmapsCount","APIServerserviceaccountsCount",
                        'APIServerclusterrolebindings.rbac.authorization.k8s.ioCount','APIServerrolebindings.rbac.authorization.k8s.ioCount',
                        'APIServerclusterroles.rbac.authorization.k8s.ioCount','APIServerroles.rbac.authorization.k8s.ioCount',
                        'APIServerleases.coordination.k8s.ioCount','APIServerconfigurationpolicies.policy.open-cluster-management.ioCount',
                        'APIServermanifestworks.work.open-cluster-management.ioCount','APIServerplacements.cluster.open-cluster-management.ioCount',
                        'APIServersubscriptions.apps.open-cluster-management.ioCount','APIServerapplications.app.k8s.ioCount',
                        'APIServerapplications.argoproj.ioCount','APIServerapplicationsets.argoproj.ioCount'])

        masterDF.plot(y=["ManagedClusterCount"], ax = ax) 
        masterDF.plot(y=y1array, ax = ax, secondary_y = True)  
        plt.title("Combined Master API Server Object Count")       
        plt.savefig(inspector_dir + '/master-apiServerObjCount.png')
    except Exception as e:
        print(Fore.RED+"Failure in drawing graph Combined Master API Server Object Count - probably metrics are missing: ",e)  
        print(Style.RESET_ALL)  
