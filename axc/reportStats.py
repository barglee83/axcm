#!/usr/bin/env python
import datetime
import random
import requests
import xmltodict
import json
import getopt
import sys


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

    lm={}
    lm['name']="HA1"                # Assuming since single just use HA1
    lm['ip'] = lmip                 # Assuming since single this will match Ip provided
    lm['mode'] = "single"           #Derived from API Call


    # DATA CPU TOTAL USER/System/Idel/IOWaiting
    # DATA Memory MBtotal/memused/MBused/percentagememused/memfree/MBfree/percentmemfree


    lmcluster['lm']=[]
    #lmcluster['lm'].append(lm)

    url = "https://" + user + ":" + password + "@" + lmip + ":" + port + "/access/get?param=Hostname"
    print(url)
    response = requests.get(url, verify=False)
    obj = xmltodict.parse(response.text)
    lmcluster['name']=obj['Response']['Success']['Data']['hostname']

    #--TEMP
    rsStatusByID={}
    url = "https://" + user + ":" + password + "@" + lmip + ":" + port + "/access/listvs"
    print(url)
    response = requests.get(url, verify=False)
    obj = xmltodict.parse(response.text)
    rslist2 = []
    for i in obj['Response']['Success']['Data']['VS']:      #Array of VS's
        currentRs = i['Rs']
        currentRs = [currentRs] if isinstance(currentRs, dict) else currentRs # convert to List if not already
        for x in currentRs:
            #print("RSID:",x['RsIndex'],"RS Status:",x['Status'],"VSID", i['Index'])
            rsStatusByID[x['RsIndex']]=x['Status']


    url = "https://" + user + ":" + password + "@" + lmip + ":" + port + "/access/stats"
    print(url)
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
        #vs['name']=i['NickName']
        vs['ip'] = i['VSAddress']
        vs['port'] = i['VSPort']
        vs['id']= int(i['Index'])
        vs['status'] = i['Status']
        vs['conns'] = int(i['TotalConns'])
        vs['activeconns'] = int(i['ActiveConns'])
        vs['connrate'] = int(i['ConnsPerSec'])
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
        rslist.append(rs)

        # get Status from Status dictionary
        rs['status'] = rsStatusByID[i['RSIndex']]


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
    print("HTTP POST")
    print(app_json)

    headers = {}
    headers['apikey']= apikey
    url = 'http://'+endpoint+'/'+custid+"_"+lmid
    print(url)
    print(headers)
    x = requests.post(url, data=app_json, headers=headers)
    print(x.text)





if __name__ == '__main__':
    main()
