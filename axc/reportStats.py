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
    short_options = "i:o:u:p:c:l:x:a:z:"
    long_options = ["help"]
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        # Output error, and return with an error code
        print(str(err))
        sys.exit(2)

    endpointport=443

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
        elif current_argument in ("-z"):
            endpointport = current_value
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
    vsidIPMap = {}
    vsidPortMap = {}
    rsStatusByID={}
    rsVsByID={}
    url = "https://" + user + ":" + password + "@" + lmip + ":" + port + "/access/listvs"
    print("reportStats.py -- LoadMaster Query",url)
    response = requests.get(url, verify=False)
    listvsobj = xmltodict.parse(response.text)
    rslist2 = []
    namelist={}


    for i in listvsobj['Response']['Success']['Data']['VS']:      #Array of VS's
        if "Rs" in i:
            currentRs = i['Rs']
            currentRs = [currentRs] if isinstance(currentRs, dict) else currentRs # convert to List if not already # Work Around Bad LoadMaster Presentation of Data
            for x in currentRs:
                print("RSID:",x['RsIndex'],"RS Status:",x['Status'],"VSID", i['Index'])
                rsStatusByID[x['RsIndex']]=x['Status']
                rsVsByID[int(x['RsIndex'])] = int(i['Index'])       # RSID-VSID
            # Get Dictionary of VS Name and IDs
        vsidNicknameMap[i['Index']]=i['NickName']
        print(vsidNicknameMap)

        print("RsStatusByID", rsStatusByID)
        print("rsVsByID", rsVsByID)





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

    print(obj['Response']['Success']['Data']['SubscriptionEntry1']['Expires'])
    print(round(time.time()))
    print(round((int(obj['Response']['Success']['Data']['SubscriptionEntry1']['Expires'])-round(time.time()))/86400))
    license['subsexpirydays'] = int(round((int(obj['Response']['Success']['Data']['SubscriptionEntry1']['Expires'])-round(time.time()))/86400))
    #license['subsexpirydays'] = round((int(obj['Response']['Success']['Data']['SubscriptionEntry1']['Expires']) - int(time.time()))/86400)

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


    disk={}
    for i in obj['Response']['Success']['Data']['DiskUsage']['partition']:
        if i['name'] == '/var/log':
            disk['varloggbtotal']=int(float(i['GBtotal'])*1000)
            disk['varloggbused'] = int(float(i['GBused'])*1000)
            disk['varloggbfree'] = int(float(i['GBfree'])*1000)
        if i['name'] == '/var/log/userlog':
            disk['varloguserlogbtotal']=int(float(i['GBtotal'])*1000)
            disk['varlogusergbused'] = int(float(i['GBused'])*1000)
            disk['varlogusergbfree'] = int(float(i['GBfree'])*1000)




    lm['cpu'] = cpu
    lm['memory'] = memory
    lm['disk'] = disk

    lmcluster['totalconns']=int(obj['Response']['Success']['Data']['VStotals']['TotalConns'])
    lmcluster['totalbits']=int(obj['Response']['Success']['Data']['VStotals']['TotalBits'])
    lmcluster['totalbytes']=int(obj['Response']['Success']['Data']['VStotals']['TotalBytes'])
    lmcluster['totalpackets']=int(obj['Response']['Success']['Data']['VStotals']['TotalPackets'])

    lmcluster['lm'].append(lm)

    vslist=[]
    subvslist=[]
    rslist=[]
    print("VSID Nickname Map",vsidNicknameMap)

    print ("Object is",obj['Response']['Success']['Data']['Vs'])

    # Get around LM behaviuor of returning wither list or single object. if one dict object convert to list
    object = [obj['Response']['Success']['Data']['Vs']] if isinstance(obj['Response']['Success']['Data']['Vs'],dict) else obj['Response']['Success']['Data']['Vs']  # convert to List if not already # Work Around Bad LoadMaster Presentation of Data


    vsidIPMap = {}
    vsidPortMap = {}

    #Parent VS's Only
    for i in object:                      #This only returns Parent VSs. It also returns different types depending on asingle Vs or Multiple.
        vs = {}
        print("i is", i)
        print ("i index is")
        print(i['Index'])
        vs['nickname']=vsidNicknameMap[i['Index']].rsplit('-',1)[0]
        vs['application'] = vsidNicknameMap[i['Index']].rsplit('-',1)[1]
        vs['loadmaster']=lmcluster['name']
        vs['ip'] = i['VSAddress']
        vs['port'] = i['VSPort']
        vs['id']= int(i['Index'])
        vs['status'] = i['Status']
        vs['type'] = 'vs'

        vsidIPMap[i['Index']] = i['VSAddress']
        vsidPortMap[i['Index']] = i['VSPort']

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

    # need to iterate through and add all SubVSs too
    # Get around LM behaviuor of returning wither list or single object. if one dict object convert to list

    listvsobject = [listvsobj['Response']['Success']['Data']['VS']] if isinstance(listvsobj['Response']['Success']['Data']['VS'],dict) else listvsobj['Response']['Success']['Data']['VS']  # convert to List if not already # Work Around Bad LoadMaster Presentation of Data


    print("\n\n\vs id map", vsidIPMap)
    for i in listvsobject:
        print("DO SECOND CHECK - i is", i)
        print ("i index is")
        print(i['Index'])
        print(i['MasterVS'])        #This Value is 0 if its a SubVS and shows count of subVSs if a master. but is also 0 if normal VS
        # Check if already in Vs List - if not add.
        print("Vslist is", vslist)
        alreadyadded=0
        for vs in vslist:
            print (vs['id'],"compare to",i['Index'])
            print (type(vs['id']), "compare to", type(i['Index']))
            if vs['id'] == int(i['Index']):
                alreadyadded=1
        if alreadyadded == 0:
            vs = {}
            vs['nickname'] = vsidNicknameMap[i['Index']].rsplit('-', 1)[0]
            vs['application'] = vsidNicknameMap[i['Index']].rsplit('-', 1)[1]
            vs['loadmaster'] = lmcluster['name']
            vs['id'] = int(i['Index'])
            vs['type'] = 'subvs'
            vs['status'] = i['Status']
            vs['rs'] = []
            if int(i['MasterVSID'])>0:
                vs['ip'] = 0                #need to inherit from MasterVS--- input VSID - get back IP
                vs['port'] = 0                #need to inherit from MasterVS
                vs['conns'] = 0                #need to inherit from RSs
                vs['packets'] = 0                #need to inherit from RSs
                vs['bytes'] = 0                #need to inherit from RSs
                vs['bits'] = 0                #need to inherit from RSs
                vs['activeconns'] = 0                #need to inherit from RSs
                vs['connrate'] = 0                #CANNOT inherit from RSs
                #print("\n\nindex is",i['Index'])
                #print(vsidIPMap['1'])
                vs['ip']=vsidIPMap[i['MasterVSID']]
                vs['port']=vsidPortMap[i['MasterVSID']]




            subvslist.append(vs)

    vslist.extend(subvslist)


    print("Final VS List",vslist)


    # Need a dict of subvs-rs's an their vsids - Stored in rsVsByID


    #print(rsVsByID)
    #print(rsVsByID[44])
    for i in obj['Response']['Success']['Data']['Rs']:
        rs = {}
        #rs['vsid'] = int(i['VSIndex'])          # Need to add a separate check to see if Rs ispart of subVS
        rs['vsid'] = rsVsByID[int(i['RSIndex'])]
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


    print("VS LIST", vslist)
    # Need to Update this to get RS Status.
    for vs in vslist:
        for rs in rslist:
            if rs['vsid']==vs['id']:
                #print(rs['ip']+"matches"+vs['ip'])
                vs['rs'].append(rs)
                #If the VS is A SubVs calcualte metrics based on Rs sums
        if vs['type']=='subvs':
            print("SubVS Match",vs)
            for rs in vs['rs']:
                vs['conns']+=rs['conns']
                vs['packets'] += rs['packets']
                vs['bytes'] += rs['conns']
                vs['bits'] += rs['packets']
                vs['activeconns'] += rs['activeconns']




    lmcluster['vs']=vslist
    #print(lmcluster)

    app_json = json.dumps(lmcluster)
    print("reportStats.py -- HTTP POST to Send")
    print(app_json)

    headers = {}
    headers['apikey']= apikey

    if (endpointport ==443):
        url = 'https://'+endpoint+'/'+custid+"_"+lmid
    else:
        url = 'http://' + endpoint + ":" + endpointport + '/' + custid + "_" + lmid
    print("reportStats.py -- AXM URL",url)
    print(headers)

    #UNCOMMENT WHEN DONE!
    x = requests.post(url, data=app_json, headers=headers, verify=False)
    print(x.text)

#
# {Custid:1001 Name:CUSTLM Lmclusterid:1
# Lm:[{Name:HA1 IP:10.0.0.9 Mode:single Cpu:{User:0 System:0 Idle:99 Iowait:0} Memory:{Memused:298740 Percentmemused:68 Memfree:134300 Percentmemfree:32}}] Vs:[{IP:10.0.0.9 Port:80 ID:1 Status:up Conns:14446 Activeconns:0 Connrate:0 Rs:[{Vsid:1 IP:10.0.0.5 Port:9081 ID:1 Activeconns:0 Connrate:0 Status:Up} {Vsid:1 IP:10.0.0.5 Port:9082 ID:2 Activeconns:0 Connrate:0 Status:Up}]} {IP:10.0.0.9 Port:443 ID:2 Status:up Conns:39 Activeconns:0 Connrate:0 Rs:[{Vsid:2 IP:10.0.0.5 Port:8081 ID:3 Activeconns:0 Connrate:0 Status:Up} {Vsid:2 IP:10.0.0.5 Port:8082 ID:4 Activeconns:0 Connrate:0 Status:Up}]}]}
#
#

if __name__ == '__main__':
    main()
