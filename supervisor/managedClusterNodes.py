
from kubernetes import client, config
from colorama import Fore, Back, Style
import sys
import utility

import pandas
#import urllib3
#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def getManagedClusterNodeCount(debug=False):
    
    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print("Gathering Node count per managed clusters")
    print("************************************************************************************************")
    print(Style.RESET_ALL)
    status = True
    mcnodeList=[]

    
    # Configs can be set in Configuration class directly or using helper utility
    config.load_incluster_config()

    v1 = client.CustomObjectsApi()
    try:
        mcs = v1.list_cluster_custom_object(group="internal.open-cluster-management.io", version="v1beta1", plural="managedclusterinfos", _request_timeout=60)
       
        for mc in mcs.get('items', []):
            mcnode={}
            if debug: print(mc['metadata']['name'])
            if debug: print(mc['status']['nodeList'])
            mcnode["managedcluster"]= mc['metadata']['name']
            i=0
            # we do not collect nodeList for all vendors
            for x in  mc['status']:
                if x=='nodeList' : 
                    for x in mc['status']['nodeList']:
                        #i=0
                        for k,v in x.items():
                            #i =0
                            if (k=="capacity"):
                                i=i+1
                    mcnode["nodeCount"]=i    
            #print(mcnode)
            mcnodeList.append(mcnode)
        
        mcnodeList_df=pandas.DataFrame.from_records(mcnodeList)
        print(mcnodeList_df.to_markdown())
        utility.saveCSV( mcnodeList_df, "managed-cluster-node-count")

        print(Back.LIGHTYELLOW_EX+"")
        print("************************************************************************************************")
        print("Gathering Node count per managed clusters")  
        print("************************************************************************************************") 
        print(Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED+"Failure: ",e) 
        sys.exit("Cluster may be down, or credentials may be wrong, or simply not connected")
        print(Style.RESET_ALL)

    return status