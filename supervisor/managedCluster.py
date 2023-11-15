from ast import And
from kubernetes import client, config
from colorama import Fore, Back, Style
import sys
import pandas
import utility

def checkManagedClusterStatus(debug=False):
    
    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print("Managed Cluster Health Check")
    print("************************************************************************************************")
    print(Style.RESET_ALL)
    status = True
    mclusters=[]
    summaryStatus= True

    # Configs can be set in Configuration class directly or using helper utility
    config.load_incluster_config()

    v1 = client.CustomObjectsApi()
    try:
        mcs = v1.list_cluster_custom_object(group="cluster.open-cluster-management.io", version="v1", plural="managedclusters",_request_timeout=60)

        for mc in mcs.get('items', []):  
            acluster={}
            acluster['managedName']=mc['metadata']['name']
            acluster['creationTimestamp']=mc['metadata']['creationTimestamp']

            #print(mc['status']['conditions'])

            for x in mc['status']['conditions']:
                ###### do we need this?
                status=True
                for k,v in x.items():
                    #status=True
                    if (k=="reason" or k=="status"):
                        if debug: print(k," : ",v)
                        if k=="status":
                            if v=="True":
                                status = status and True
                            else:
                                status = False
                                summaryStatus = False    
                        acluster['health']=status        
            #print("\n")

            mclusters.append(acluster)
            if debug: print(acluster)
            #print("++++++++++++++++++++++++++++++++++++++++++++++")
        #print(mclusters)
        # This just gives the status of the mananged clusters - not the addons yet
        mclusters_df = pandas.DataFrame.from_records(mclusters)  
        print(mclusters_df.to_markdown()) 
        utility.saveCSV(mclusters_df, "managed-cluster-list")

        if False in mclusters_df["health"].values :
            print("\n Problematic Clusters")
            print(mclusters_df[mclusters_df["health"] != True])
            status= False

        print(Back.LIGHTYELLOW_EX+"")
        print("************************************************************************************************")
        print("Managed Cluster Health Check passed ============ ", summaryStatus)
        print("************************************************************************************************")
        print(Style.RESET_ALL)

        print(Back.LIGHTYELLOW_EX+"")
        print("************************************************************************************************")
        print("Managed Cluster Addon Health Check")
        print("************************************************************************************************")
        print(Style.RESET_ALL)

        if len(mclusters) < 500 :
            # This gives the addon status for each managed cluster.
            managedClusterAddonList=[]
            for x in mclusters:
                for k,v in x.items():
                    if (k=="managedName") :
                        managedClusterAddon = checkManagedClusterAddonStatus(v,debug)
                        managedClusterAddonList.append(managedClusterAddon)
        
            managedClusterAddonList_df = pandas.DataFrame.from_records(managedClusterAddonList)  
            if debug: print(managedClusterAddonList_df.to_markdown()) 
            utility.saveCSV(managedClusterAddonList_df, "Managed-cluster-addon-list")

            analyzeAddonHealth(managedClusterAddonList_df,debug)
        else:
            print("Skippinng Managed cluster Addon Health Check because there are more than 500 managed clusters")    

    except Exception as e:
        print(Fore.RED+"Failure: ",e) 
        sys.exit("Cluster may be down, or credentials may be wrong, or simply not connected")   
        print(Style.RESET_ALL)

    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print(" Managed Cluster Addon Health Check passed ============ ", summaryStatus)
    print("************************************************************************************************")
    print(Style.RESET_ALL)

    return status

def analyzeAddonHealth(mcAddonList_df, debug) :

    print("Summarazing the Addon Healths on Managed clusters \n")
    print("Raw data in csv form for manual analysis is saved in output\breakdown\Managed-cluster-addon-list.csv \n")
    #print(mcAddonList_df.dtypes)

    # Iterate over the dataframe columns
    for column in mcAddonList_df :
        if column != 'managedName' :
            columnSeriesObj = mcAddonList_df[column]
            print('\nAddon Name : ', column)
            #print(columnSeriesObj.value_counts(dropna=False))
            print("Number of Managed clusters with Healthy addon: ",(columnSeriesObj.values == True).sum())
            print("Number of Managed clusters with Unhealthy addon: ",(columnSeriesObj.values == False).sum())
            print("Number of Managed clusters with Not installed addon: ",(columnSeriesObj.isna().sum().sum()))
            if debug: print('Managed clusters breakdown : ', columnSeriesObj.values)

def checkManagedClusterAddonStatus(managedCluster, debug=False): 

    status = True
    summaryStatus = True
    #print("Checking Addon Health of ",managedCluster) 
    addonCluster={}
    addonCluster['managedName']=managedCluster
    
    # Configs can be set in Configuration class directly or using helper utility
    config.load_incluster_config()
    try:

        v1 = client.CustomObjectsApi()
        mcs = v1.list_namespaced_custom_object(group="addon.open-cluster-management.io", version="v1alpha1", plural="managedclusteraddons", namespace=managedCluster,_request_timeout=60)
        for mc in mcs.get('items', []):
            #print("\n")
            if debug: print(mc['metadata']['name'])
            #print(mc['metadata']['creationTimestamp'])
            status=True
            for x in mc['status']['conditions']:
                #### do we need this
                #status=True
                for k,v in x.items():
                    if (k=="reason" or k=="status"):
                        if debug: print(k," : ",v)
                        if k=="status":
                            if v=="True":
                                status = status and True
                                #print(status)
                            else:
                                status = False 
                                summaryStatus = False
                                #print(status)   
            #print("\n")
                            addonCluster[mc['metadata']['name']]=status

        #print(addonCluster)  
    except Exception as e:
        print(Fore.RED+"Failure: ",e)
        sys.exit("Cluster may be down, or credentials may be wrong, or simply not connected")
        print(Style.RESET_ALL)
    
    # This print will not scal if we have 10s of clusters
    #print(addonCluster)
    # print(Back.LIGHTYELLOW_EX+"")
    # print("************************************************************************************************")
    # print(" Managed Cluster Addon Health Check passed ============ ", summaryStatus)
    # print("************************************************************************************************")
    # print(Style.RESET_ALL)
    # not returning status for now.
    return addonCluster