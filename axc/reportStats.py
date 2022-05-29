#!/usr/bin/env python
import datetime
import random
import requests
import xmltodict
import json
import getopt
import sys
import time


def main():
    full_cmd_arguments = sys.argv
    argument_list = full_cmd_arguments[1:]
    short_options = "i:o:u:p:c:l:x:a:"
    long_options = ["help"]
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        # Output error, and return with an error code
        print(str(err))
        sys.exit(2)

    for current_argument, current_value in arguments:
        if current_argument in ("-i"):
            lmip=current_value
        elif current_argument in ("-o"):
            port = current_value
        elif current_argument in ("-u"):
            user = current_value
        elif current_argument in ("-p"):
            password = current_value
        elif current_argument in ("-c"):
            custid = current_value
        elif current_argument in ("-l"):
            lmid = current_value
        elif current_argument in ("-x"):
            endpoint = current_value
        elif current_argument in ("-a"):
            apikey = current_value
        #elif current_argument in ("-m"):
        #    lmclusterid = current_value

    ## Query AxF for Latest config using lmid and custid

    lmcluster={}       # Full Dict Rep of a LoadMaster state and Metrics

    # For Now only support Single LoadMasters.

    lmcluster['custid']=int(custid)
    lmcluster['name']="LoadMaster"
    lmcluster['lmclusterid']=int(lmid)
    lmcluster['mode'] = "single"           #Derived from API Call


    lm={}
    lm['name']="HA1"                # Assuming since single just use HA1
    lm['ip'] = lmip                 # Assuming since single this will match Ip provided
    lm['model'] = "VLM5000"  # Derived from API Call


    # DATA CPU TOTAL USER/System/Idel/IOWaiting
    # DATA Memory MBtotal/memused/MBused/percentagememused/memfree/MBfree/percentmemfree


    lmcluster['lm']=[]
    #lmcluster['lm'].append(lm)

    url = "https://" + user + ":" + password + "@" + lmip + ":" + port + "/access/get?param=Hostname"
    print("reportStats.py -- LoadMaster Query", url)
    response = requests.get(url, verify=False)
    obj = xmltodict.parse(response.text)
    lmcluster['name']=obj['Response']['Success']['Data']['hostname']



    #/access/get?param=version





    #--TEMP
    vsidNicknameMap={}
    rsStatusByID={}
    url = "https://" + user + ":" + password + "@" + lmip + ":" + port + "/access/listvs"
    print("reportStats.py -- LoadMaster Query",url)
    response = requests.get(url, verify=False)
    obj = xmltodict.parse(response.text)
    rslist2 = []
    namelist={}
    for i in obj['Response']['Success']['Data']['VS']:      #Array of VS's
        currentRs = i['Rs']
        currentRs = [currentRs] if isinstance(currentRs, dict) else currentRs # convert to List if not already # Work Around Bad LoadMaster Presentation of Data
        for x in currentRs:
            #print("RSID:",x['RsIndex'],"RS Status:",x['Status'],"VSID", i['Index'])
            rsStatusByID[x['RsIndex']]=x['Status']

        # Get Dictionary of VS Name and IDs
        vsidNicknameMap[i['Index']]=i['NickName']
        print(vsidNicknameMap)





    url = "https://" + user + ":" + password + "@" + lmip + ":" + port + "/access/get?param=version"
    print("reportStats.py -- LoadMaster Query", url)
    response = requests.get(url, verify=False)
    obj = xmltodict.parse(response.text)
    lm['firmware']=obj['Response']['Success']['Data']['version']


    license={}

    url = "https://" + user + ":" + password + "@" + lmip + ":" + port + "/access/licenseinfo"
    print("reportStats.py -- LoadMaster Query", url)
    response = requests.get(url, verify=False)
    obj = xmltodict.parse(response.text)

    license['substier'] = obj['Response']['Success']['Data']['LicenseType']
    license['subsexpiry'] = obj['Response']['Success']['Data']['SupportUntil']
    license['subsexpirydays'] = int(round((int(obj['Response']['Success']['Data']['SubscriptionEntry1']['Expires']) - int(time.time()))/86400))

    lm['license'] = license

    url = "https://" + user + ":" + password + "@" + lmip + ":" + port + "/access/stats"
    print("reportStats.py -- LoadMaster Query",url)
    response = requests.get(url, verify=False)
    obj = xmltodict.parse(response.text)

    cpu={}
    cpu['user']= int(obj['Response']['Success']['Data']['CPU']['total']['User'])
    cpu['system'] = int(obj['Response']['Success']['Data']['CPU']['total']['System'])
    cpu['idle'] = int(obj['Response']['Success']['Data']['CPU']['total']['Idle'])
    cpu['iowait'] = int(obj['Response']['Success']['Data']['CPU']['total']['IOWaiting'])

    memory={}
    memory['memused']= int(obj['Response']['Success']['Data']['Memory']['memused'])
    memory['percentmemused'] = int(obj['Response']['Success']['Data']['Memory']['percentmemused'])
    memory['memfree'] = int(obj['Response']['Success']['Data']['Memory']['memfree'])
    memory['percentmemfree'] = int(obj['Response']['Success']['Data']['Memory']['percentmemfree'])


    lm['cpu'] = cpu
    lm['memory'] = memory





    lmcluster['lm'].append(lm)

    vslist=[]
    rslist=[]
    for i in obj['Response']['Success']['Data']['Vs']:
        vs = {}
        vs['nickname']=vsidNicknameMap[i['Index']]
        vs['loadmaster']=lmcluster['name']
        vs['ip'] = i['VSAddress']
        vs['port'] = i['VSPort']
        vs['id']= int(i['Index'])
        vs['status'] = i['Status']

        # Sample Data
        vs['statuscode'] = 2            #0 is up. 1 LOR 2 DOWN
        vs['conns'] = int(i['TotalConns'])
        vs['packets'] = int(i['TotalPkts'])
        vs['bytes'] = int(i['TotalBytes'])
        vs['bits'] = int(i['TotalBits'])
        vs['activeconns'] = int(i['ActiveConns'])
        vs['connrate'] = int(i['ConnsPerSec'])
        #print(i['RttGlbAvg'])
        #vs['avertt'] = int(i['RttGlbAvg'])
        vs['rs']=[]
        vslist.append(vs)

    for i in obj['Response']['Success']['Data']['Rs']:
        rs = {}
        rs['vsid'] = int(i['VSIndex'])
        rs['ip'] = i['Addr']
        rs['port'] = i['Port']
        rs['id'] = int(i['RSIndex'])
        rs['activeconns'] = int(i['ActivConns'])
        rs['connrate'] = int(i['ConnsPerSec'])
        rs['conns'] = int(i['Conns'])
        rs['packets'] = int(i['Pkts'])
        rs['bytes'] = int(i['Bytes'])
        rs['bits'] = int(i['Bits'])
        #rs['avertt'] = int(i['RttGlbAvg'])

        rslist.append(rs)

        # get Status from Status dictionary
        rs['status'] = rsStatusByID[i['RSIndex']]
        rs['statuscode'] = 0            #0 up 1 unavailalble




    #print(vslist)
    #print("--")
    #print(rslist)


    # Need to Update this to get RS Status.
    for vs in vslist:
        for rs in rslist:
            if rs['vsid']==vs['id']:
                #print(rs['ip']+"matches"+vs['ip'])
                vs['rs'].append(rs)

    lmcluster['vs']=vslist
    #print(lmcluster)

    app_json = json.dumps(lmcluster)
    print("reportStats.py -- HTTP POST to Send")
    print(app_json)

    headers = {}
    headers['apikey']= apikey
    url = 'https://'+endpoint+'/'+custid+"_"+lmid
    print("reportStats.py -- AXM URL",url)
    print(headers)
    x = requests.post(url, data=app_json, headers=headers, verify=False)
    print(x.text)






#
# {Custid:1001 Name:CUSTLM Lmclusterid:1
# Lm:[{Name:HA1 IP:10.0.0.9 Mode:single Cpu:{User:0 System:0 Idle:99 Iowait:0} Memory:{Memused:298740 Percentmemused:68 Memfree:134300 Percentmemfree:32}}] Vs:[{IP:10.0.0.9 Port:80 ID:1 Status:up Conns:14446 Activeconns:0 Connrate:0 Rs:[{Vsid:1 IP:10.0.0.5 Port:9081 ID:1 Activeconns:0 Connrate:0 Status:Up} {Vsid:1 IP:10.0.0.5 Port:9082 ID:2 Activeconns:0 Connrate:0 Status:Up}]} {IP:10.0.0.9 Port:443 ID:2 Status:up Conns:39 Activeconns:0 Connrate:0 Rs:[{Vsid:2 IP:10.0.0.5 Port:8081 ID:3 Activeconns:0 Connrate:0 Status:Up} {Vsid:2 IP:10.0.0.5 Port:8082 ID:4 Activeconns:0 Connrate:0 Status:Up}]}]}
#
#
#
#
#



if __name__ == '__main__':
    main()
