from prometheus_api_client import *
#import prometheus_api_client
import datetime
import sys
import numpy as np
import pandas
import utility
from colorama import Fore, Back, Style
import matplotlib.pyplot as plt

def checkAPIServerObjects(startTime, endTime, step):
    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print("API Server Object Check")
    pc=utility.promConnect()
    print("************************************************************************************************")
    print(Style.RESET_ALL)
    status = True


    status=apiServerObjectCount(pc,startTime, endTime, step)

    
    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print(" API Server Object Check  - ", "PLEASE CHECK to see if the results are concerning!!")
    print("************************************************************************************************")
    print(Style.RESET_ALL)
    return status

# this module is done so that we can plot each individual key resource count 
# with time. We could probably use the other query in apiServer module and pivot.
# However this allows to explicitly watch resources we think are critical.
def apiServerObjectCount(pc,startTime, endTime, step):

    print("Key APi Server Objects Count")
    objects=['secrets','configmaps','serviceaccounts','clusterrolebindings.rbac.authorization.k8s.io','rolebindings.rbac.authorization.k8s.io',
             'clusterroles.rbac.authorization.k8s.io','roles.rbac.authorization.k8s.io','leases.coordination.k8s.io',
             'configurationpolicies.policy.open-cluster-management.io','manifestworks.work.open-cluster-management.io',
             'placements.cluster.open-cluster-management.io','subscriptions.apps.open-cluster-management.io','applications.app.k8s.io',
             'applications.argoproj.io','applicationsets.argoproj.io']
    for obj in objects:
        print("We are checking for ",obj)
        leading_query = 'sum(apiserver_storage_objects{resource="'
        trailing_query = '"})'
        current_query = leading_query + obj + trailing_query
        figName = utility.inspector_dir + '/apiserver-resource-' + obj + '.png'
        csvName= 'apiserver-resource-' + obj
        metricName = 'APIServer' +obj + 'Count'
        titleName= 'Trend of API Server ' + obj + ' Count'
        #print(current_query)
        #print(figName)
        #print(csvName)

        try:
            apiserver_obj_count = pc.custom_query(
                query=current_query)
            
            apiserver_obj_count_df = MetricSnapshotDataFrame(apiserver_obj_count)
            apiserver_obj_count_df["value"]=apiserver_obj_count_df["value"].astype(float)
            apiserver_obj_count_df.rename(columns={"value": metricName}, inplace = True)
            print(apiserver_obj_count_df[[metricName]].to_markdown())

            apiserver_data_trend = pc.custom_query_range(
            query=current_query,
                start_time=startTime,
                end_time=endTime,
                step=step,
            )

            apiserver_data_trend_df = MetricRangeDataFrame(apiserver_data_trend)
            apiserver_data_trend_df["value"]=apiserver_data_trend_df["value"].astype(float)
            apiserver_data_trend_df.index= pandas.to_datetime(apiserver_data_trend_df.index, unit="s")
            #apiserver_data_trend_df =  apiserver_data_trend_df.pivot( columns='resource',values='value')
            apiserver_data_trend_df.rename(columns={"value": metricName}, inplace = True)
            apiserver_data_trend_df.plot(title=titleName,figsize=(30, 15))
            plt.savefig(figName)
            utility.saveCSV(apiserver_data_trend_df, csvName,True)
            plt.close('all')
        except Exception as e:
            print(Fore.RED+"Error in getting API Server Object Count: ",e)
            print(Style.RESET_ALL)
    
        print("=============================================")
    
    status=True
    return status  

