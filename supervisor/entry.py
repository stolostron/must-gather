    
from mch import *       
from container import *
from sizing import *
from managedCluster import *
from node import *
from apiServer import *
from etcd import *
from cpuAnalysis import *
from memoryAnalysis import *
from thanos import *
from apiServerObjects import *
from managedClusterNodes import *
from colorama import Fore, Back, Style
import urllib3
import sys
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from datetime import datetime
import matplotlib.pyplot as plt
import os

#Fore(text color)	BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
#Back(for highlight)	BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
#Style	DIM, NORMAL, BRIGHT, RESET_ALL

# pass debug(boolean) as env
def main():
    start_time=(datetime.now() - timedelta(days=7))
    end_time=datetime.now()
    #start_time=dt.datetime(2021, 7, 31, 21, 30, 0, tzinfo=query.getUTC())
    #end_time=dt.datetime(2021, 8, 1, 12, 25, 0, tzinfo=query.getUTC())
    step='1m'
    tsdb = sys.argv[1]

    now = datetime.now()
    #print(Fore.MAGENTA+"")
    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print("Starting date for this ACM Health Check  - ",now)
    print("Starting datetime for History collection - ", start_time)
    print("End date and time for History collection - ", end_time)
    print(f"Parameters passed to the script : ", tsdb)
    print("************************************************************************************************")
    print(Style.RESET_ALL)
   
    utility.createSubdir()
    mch = checkMCHStatus()
    node = checkNodeStatus()

    if tsdb == "prom" : #if route is cluster prom
         cont = checkACMContainerStatus(start_time, end_time, step)
         api = checkAPIServerStatus(start_time, end_time, step)
         etcd = checkEtcdStatus(start_time, end_time, step)
         cpu = checkCPUUsage(start_time, end_time, step)
         memory = checkMemoryUsage(start_time, end_time, step)
         thanos = checkThanosStatus(start_time, end_time, step)
         apiObjet = checkAPIServerObjects(start_time, end_time, step)
    else: #if route is observability thanos
         # does not work yet
         sizing = checkACMHubClusterUtilization() 
    
    mc = checkManagedClusterStatus()
    getManagedClusterNodeCount()
    utility.saveMasterDF()

    print(Back.LIGHTYELLOW_EX+"")
    print("************************************************************************************************")
    print("End ACM Health Check")
    print("************************************************************************************************")
    print(Style.RESET_ALL)
if __name__ == "__main__":
    main()
