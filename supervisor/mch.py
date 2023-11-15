
from kubernetes import client, config
from colorama import Fore, Back, Style
import sys
#import urllib3
#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def checkMCHStatus(debug=False):
    
    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print("MCH Operator Health Check")
    print("************************************************************************************************")
    print(Style.RESET_ALL)
    status = True
    mch={}
    
    # Configs can be set in Configuration class directly or using helper utility
#    config.load_incluster_config()
    config.load_incluster_config()
    v1 = client.CustomObjectsApi()
    try:
        mcs = v1.list_namespaced_custom_object(group="operator.open-cluster-management.io", version="v1", plural="multiclusterhubs", namespace="open-cluster-management", _request_timeout=1)

        for mc in mcs.get('items', []):
            #print("\n")
            if debug: print(mc['metadata']['name'])
            if debug: print("Current Version: ",mc['status']['currentVersion'])
            if debug: print("Desired Version: ",mc['status']['desiredVersion'])
            if debug: print("Phase: ",mc['status']['phase'])
            mch['name']=mc['metadata']['name']
            mch['CurrentVersion']=mc['status']['currentVersion']
            mch['DesiredVersion']=mc['status']['desiredVersion']
            mch['Phase']=mc['status']['phase']
            for x in mc['status']['conditions']:
                for k,v in x.items():
                    if (k=="reason" or k=="status"):
                        if debug: print(k," : ",v)
                        if k=="status":
                            if v=="True":
                                status = status & True
                            else:
                                status = status & False    
            #print("\n")
            mch['Health']=status
            print(mch)
        
        print(Back.LIGHTYELLOW_EX+"")
        print("************************************************************************************************")
        print("MCH Operator Health Check = ", status)  
        print("************************************************************************************************") 
        print(Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED+"Failure: ",e) 
        sys.exit("Cluster may be down, or credentials may be wrong, or simply not connected")
        print(Style.RESET_ALL)

    return status
