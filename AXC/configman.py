#!/usr/bin/env python
import datetime
import random
import requests
import xmltodict
import json
import getopt
import sys
import os

def main():

    endpoint="dev.ax.barglee.com"
    filepath=""
    full_cmd_arguments = sys.argv
    argument_list = full_cmd_arguments[1:]
    short_options = "i:o:u:p:c:l:x:z:a:"
    long_options = ["help"]
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        # Output error, and return with an error code
        print(str(err))
        sys.exit(2)

    for current_argument, current_value in arguments:
        if current_argument in ("-i"):
            lmip= current_value
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
        elif current_argument in ("-z"):
            filepath = current_value
        elif current_argument in ("-a"):
            apikey = current_value

    ### Config Management
    ## Get Last time config changed
    ## file structure lmconfig_<custid>_<lmid>.json
    print("lmconfig_"+custid+"_"+lmid+".json")

    if not os.path.exists(filepath+"lmconfig_"+custid+"_"+lmid+".json"):
        #open(filepath+"lmconfig_"+custid+"_"+lmid+".json", 'w').close()
        myfile=open(filepath+"lmconfig_"+custid+"_"+lmid+".json", 'w')
        myfile.write("""{"motd": "Message of the Day", "name": "Hostname", "time": 0}\n""")
        myfile.close()

    with open(filepath+"lmconfig_"+custid+"_"+lmid+".json") as json_file:
            conf = json.load(json_file)
    print("Local Config")
    print(conf["time"])
    print(conf["name"])

    headers = {}
    headers['apikey']= apikey
    print(headers)

    url = "http://"+endpoint+"/"+custid+"_"+lmid
    response = requests.get(url,headers=headers)
    latestconfig = json.loads(response.text)
    print("Cloud Config")
    print(latestconfig)

    if latestconfig["time"]>conf["time"]:
        print("Update Needed")
        f = open("lmconfig_"+custid+"_"+lmid+".json", "w")
        print(json.dumps(latestconfig))
        f.write(json.dumps(latestconfig))
        f.close()
        url="https://"+user+":"+password+"@"+lmip+":"+port+"/access/set?param=Hostname&value="+latestconfig["name"]
        print(url)
        response = requests.get(url, verify=False)
        print(response)
        url="https://"+user+":"+password+"@"+lmip+":"+port+"/access/set?param=motd&value="+latestconfig["motd"]
        print(url)
        response = requests.get(url, verify=False)
        print(response)
        with open("lmconfig_" + custid + "_" + lmid + ".json") as json_file:
            conf = json.load(json_file)
        print("Local Config Now")
        print(conf["time"])
        print(conf["name"])




if __name__ == '__main__':
    main()
