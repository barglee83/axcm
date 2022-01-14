#!/usr/bin/env python
import time
import re
import sys
import getopt


def main():
    full_cmd_arguments = sys.argv
    argument_list = full_cmd_arguments[1:]
    short_options = "c:l:i:o:"
    long_options = ["help"]
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        # Output error, and return with an error code
        print(str(err))
        sys.exit(2)

    for current_argument, current_value in arguments:
        if current_argument in ("-c"):
            custid = current_value
        elif current_argument in ("-l"):
            lmid = current_value
        elif current_argument in ("-i"):
            infile = current_value
        elif current_argument in ("-o"):
            outfile = current_value

    file = open(infile,"r")
    newconnregex="(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): (SSL accept on|Accept on) (.*?..*?..*?..*?):(\w{1,5}) from (.*?..*?..*?..*?):(\w{1,5})?(.*)"
    ## Requirement - Global Extended L7 Debug enabled. VS Extended Debug set to any level
    rttconnregex="(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): Conn: dest RTT ([0-9]*)\/([0-9]*) us min ([0-9]*) us"
    ## Requirement - Global Extended L7 Debug enabled. VS Extended Debug set to any level

    closeregex="(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): conn release 7"
    ## Requirement - Global Extended L7 Debug enabled. VS Extended Debug set to any level

    sslcipherregex="(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): got sni '(.*)' cipher '(.*)'"
    ## Requirement - Global Extended L7 Debug enabled. VS Extended Debug set to any level
    ## Requirement - Add Received Cipher Name Set on VS
    # Group 3SNI Name Group 4 Cipher


    tlsversionregex="(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): ## X-SSL-Protocol: (.*)"
    ## Requirement - Global Extended L7 Debug enabled. VS Extended Debug set to Full Debg + Headers



    useragentregex="(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): User-Agent: (.*)"
    ## Requirement - Global Extended L7 Debug enabled. VS Extended Debug set to any level
    ## Requirement - Global Extended L7 Debug enabled. VS Extended Debug set to Full Debug

    # Group 3 UA

    persistregex="(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): find persist returns (.*)"
    #GROUP 3 Persist Token
    ## Requirement - Global Extended L7 Debug enabled. VS Extended Debug set to any level
    ## Requirement - Global Extended L7 Debug enabled. VS Extended Debug set to Full Debug

    queryregex="(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): request: (.*) (.*)"
    #G3 Request method G4 URL

    rsregex="(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): Connecting from (.*?..*?..*?..*?):(\w{1,5}) to (.*?..*?..*?..*?):(\w{1,5})"
    # OR Jan 10 23:24:44 1002LM60NewHostname kernel: L7: ffff88806f5ba040: Connecting from 10.1.151.218:30339 to 10.1.151.171:80 NAT NAT at end add ~(.*) maybe and detect trans
    #G5 RSIP G6 RSPORT

    conreqresregex="(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): Conn: Request ([0-9])* ms Response ([0-9])* ms"
    #G3 Req G4 Res
    xfwdfor = "(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): ## X-Forwarded-For: (.*)"
    # G3 XFWDHEADER
    ## Requirement - Global Extended L7 Debug enabled. VS Extended Debug set to Full Debg + Headers

    xfwdforport = "(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): ## X-Forwarded-For-Port: (.*)"
    # G3 XFWDPORTHEADER

    fullheaderblob = "(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): ## (.*)"
    ##SHOULD APPEND G3


    statuscodessl = "(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): ok_to_compress ([0-9]+)"
    statuscodenonssl = "(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): mangle_response [0-9]* \(Response ([0-9]+)\)"
    #(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): mangle_response [0-9]* \(Response (.*)\)

    # For HTTP - Jan 13 07:01:28 1002LM60NewHostname kernel: L7: ffff888074367ca8: mangle_response 187 (Response 404)
    ##SHOULD APPEND G3
    ## XROOT login - echo 25 > /proc/sys/net/l7/debug_level
    ## Need to ensure Some Response Processing being done e.g. Response Body Modification Rule Applied on VS

    dict={}
    #keys=["time","clientip", "clientport", "vsip", "vsport", "dstrtt1", "dstrtt2", "rttmin","ua", "persist", "querymethod", "queryurl", "rsip", "rsport", "requesttime", "responsetime", "xfwdfor", "xfwdforport", "statuscode"]
    #for last_line in file:
    #    pass





    while 1:
        where = file.tell()
        #print("line loc is", where)
        line = file.readline()
        #print("line is", line)
        if not line:
            time.sleep(1)
            file.seek(where)
        else:
            m = re.match(newconnregex, line)
            if m:
                logtime = m.group(1)
                connid = m.group(2)
                ssl =0
                print(m.group(3))
                if ("SSL" in m.group(3)):
                    ssl=1
                clientip= m.group(6)
                clientport=m.group(7)
                vsip= m.group(4)
                vsport=m.group(5)
                #newsession={key: "" for key in keys}
                newsession={}
                newsession["time"]=logtime
                newsession["ssl"]=ssl
                newsession["clientip"]=clientip
                newsession["clientport"]=clientport
                newsession["vsip"]=vsip
                newsession["vsport"] = vsport
                newsession["dstrtt1"]=0
                newsession["dstrtt2"]=0
                newsession["rttmin"]=0
                newsession["ua"] = "\"none\""
                newsession["persist"] = "none"
                newsession["querymethod"] = "unknown"
                newsession["queryurl"] = "/"
                newsession["rsip"] = "0.0.0.0"
                newsession["rsport"] = "0"
                newsession["requesttime"] = 0
                newsession["responsetime"] = 0
                newsession["xfwdfor"] = "255.255.255.255"
                newsession["xfwdforport"] = 0
                newsession["statuscode"] = 0
                newsession["sslcipher"] = "unknown"
                newsession["sslsni"] = "unknown"
                newsession["tlsversion"] = "unknown"
                dict[connid]=newsession

            elif re.match(rttconnregex, line):
                n=re.match(rttconnregex, line)
                print("Match RTT")
                lineconnid = n.group(2)
                if lineconnid in dict.keys():
                    dict[lineconnid]["dstrtt1"] = n.group(3)
                    dict[lineconnid]["dstrtt2"] = n.group(4)
                    dict[lineconnid]["rttmin"] = n.group(5)
            elif re.match(useragentregex, line):
                n=re.match(useragentregex, line)
                print("Match UA")
                lineconnid = n.group(2)
                if lineconnid in dict.keys():
                    dict[lineconnid]["ua"] = "\""+n.group(3)+"\""
            elif re.match(persistregex, line):
                    n = re.match(persistregex, line)
                    print("Match Persist")
                    lineconnid = n.group(2)
                    if lineconnid in dict.keys():
                        dict[lineconnid]["persist"] = n.group(3)
            elif re.match(sslcipherregex, line):
                    n = re.match(sslcipherregex, line)
                    print("Match sslcipherregex")
                    lineconnid = n.group(2)
                    if lineconnid in dict.keys():
                        dict[lineconnid]["sslcipher"] = n.group(4)
                        dict[lineconnid]["sslsni"] = n.group(3)
            elif re.match(tlsversionregex, line):
                    n = re.match(tlsversionregex, line)
                    print("Match tlsversionregex")
                    lineconnid = n.group(2)
                    if lineconnid in dict.keys():
                        dict[lineconnid]["tlsversion"] = n.group(3)
            elif re.match(queryregex, line):
                    n = re.match(queryregex, line)
                    print("Match queryregex")
                    lineconnid = n.group(2)
                    if lineconnid in dict.keys():
                        dict[lineconnid]["querymethod"] = n.group(3)
                        dict[lineconnid]["queryurl"] = n.group(4)
            elif re.match(rsregex, line):
                    n = re.match(rsregex, line)
                    print("Match rsregex")
                    lineconnid = n.group(2)
                    if lineconnid in dict.keys():
                        dict[lineconnid]["rsip"] = n.group(5)
                        dict[lineconnid]["rsport"] = n.group(6)
            elif re.match(conreqresregex, line):
                    n = re.match(conreqresregex, line)
                    print("Match conreqresregex")
                    lineconnid = n.group(2)
                    if lineconnid in dict.keys():
                        dict[lineconnid]["requesttime"] = n.group(3)
                        dict[lineconnid]["responsetime"] = n.group(4)
            elif re.match(xfwdfor, line):
                    n = re.match(xfwdfor, line)
                    print("Match xfwdfor")
                    lineconnid = n.group(2)
                    if lineconnid in dict.keys():
                        dict[lineconnid]["xfwdfor"] = n.group(3)
            elif re.match(xfwdforport, line):
                    n = re.match(xfwdforport, line)
                    print("Match xfwdforport")
                    lineconnid = n.group(2)
                    if lineconnid in dict.keys():
                        dict[lineconnid]["xfwdforport"] = n.group(3)
            elif re.match(statuscodessl, line):
                    n = re.match(statuscodessl, line)
                    print("Match statuscode ssl")
                    lineconnid = n.group(2)
                    if lineconnid in dict.keys():
                        if dict[lineconnid]["statuscode"] == 0:
                            dict[lineconnid]["statuscode"] = n.group(3)
            elif re.match(statuscodenonssl, line):
                    n = re.match(statuscodenonssl, line)
                    print("Match statuscode non ssl")
                    lineconnid = n.group(2)
                    if lineconnid in dict.keys():
                        if dict[lineconnid]["statuscode"] == 0:
                            dict[lineconnid]["statuscode"] = n.group(3)
            elif re.match(closeregex,line):
                o = re.match(closeregex,line)
                if o:
                    print("Match Close")
                    lineconnid = o.group(2)
                    if lineconnid in dict.keys():
                        print ("Completed Object",dict[lineconnid])
                        fields = [dict[lineconnid]["time"],
                                  "l7",
                                  custid,
                                  lmid,
                                  str(dict[lineconnid]["ssl"]),
                                  dict[lineconnid]["clientip"],
                                  dict[lineconnid]["clientport"],
                                  dict[lineconnid]["vsip"],
                                  dict[lineconnid]["vsport"],
                                  str(dict[lineconnid]["dstrtt1"]),
                                  str(dict[lineconnid]["dstrtt2"]),
                                  str(dict[lineconnid]["rttmin"]),
                                  dict[lineconnid]["ua"],
                                  dict[lineconnid]["persist"],
                                  dict[lineconnid]["queryurl"],
                                  dict[lineconnid]["querymethod"],
                                  dict[lineconnid]["rsip"],
                                  dict[lineconnid]["rsport"],
                                  str(dict[lineconnid]["requesttime"]),
                                  str(dict[lineconnid]["responsetime"]),
                                  dict[lineconnid]["xfwdfor"],
                                  str(dict[lineconnid]["xfwdforport"]),
                                  str(dict[lineconnid]["statuscode"]),
                                  dict[lineconnid]["sslcipher"],
                                  dict[lineconnid]["sslsni"],
                                  dict[lineconnid]["tlsversion"]
                                  ]

                        print("FIELDS")
                        print(fields)
                        print("DICT")
                        print(dict[lineconnid])
                        out = open(outfile, "a")
                        out.write(','.join(fields))
                        out.write("\n")
                        out.close()
                        del dict[lineconnid]


                #print(lineconnid,dstrtt1, dstrtt2,rttmin)

            #print(line) # already has newline
if __name__ == '__main__':
    main()
