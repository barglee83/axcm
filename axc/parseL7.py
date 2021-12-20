#!/usr/bin/env python
import time
import re
import sys
import getopt


def main():
    full_cmd_arguments = sys.argv
    argument_list = full_cmd_arguments[1:]
    short_options = "c:l:"
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

    file = open("/var/log/LoadMaster.log","r")
    newconnregex="(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): (SSL accept on|Accept on) (.*?..*?..*?..*?):(\w{1,5}) from (.*?..*?..*?..*?):(\w{1,5})?(.*)"
    rttconnregex="(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): Conn: dest RTT ([0-9]*)\/([0-9]*) us min ([0-9]*) us"
    closeregex="(.*) [a-zA-Z0-9_.-]* kernel: L7: ([a-zA-Z0-9_.-]{16}): conn release 7"

    dict={}

    #for last_line in file:
    #    pass

    while 1:
        where = file.tell()
        print("line loc is", where)
        line = file.readline()
        print("line is", line)
        if not line:
            time.sleep(1)
            file.seek(where)
        else:
            m = re.match(newconnregex, line)
            if m:
                logtime = m.group(1)
                connid = m.group(2)
                clientip= m.group(6)
                clientport=m.group(7)
                vsip= m.group(4)
                vsport=m.group(5)
                newsession={}
                newsession["time"]=logtime
                newsession["clientip"]=clientip
                newsession["clientport"]=clientport
                newsession["vsip"]=vsip
                newsession["vsport"] = vsport
                newsession["dstrtt1"]=0
                newsession["dstrtt2"]=0
                newsession["rttmin"]=0
                dict[connid]=newsession
                #print(dict)
            else:
                n = re.match(rttconnregex, line)
                if n:
                    print("Match RTT")
                    lineconnid = n.group(2)
                    dstrtt2 = n.group(4)
                    rttmin = n.group(5)
                    if lineconnid in dict.keys():
                        dict[lineconnid]["dstrtt1"] = n.group(3)
                        dict[lineconnid]["dstrtt2"] = n.group(4)
                        dict[lineconnid]["rttmin"] = n.group(5)
                        #print(dict)
                else:
                    o = re.match(closeregex,line)
                    if o:
                        print("Match Close")
                        lineconnid = o.group(2)
                        if lineconnid in dict.keys():
                            print ("Completed Object",dict[lineconnid])
                            fields = [dict[lineconnid]["time"], "l7", custid, lmid, dict[lineconnid]["clientip"], dict[lineconnid]["clientport"], dict[lineconnid]["vsip"], dict[lineconnid]["vsport"], str(dict[lineconnid]["dstrtt1"]), str(dict[lineconnid]["dstrtt2"]), str(dict[lineconnid]["rttmin"])]
                            out = open("l7.log", "a")
                            out.write(','.join(fields))
                            out.write("\n")
                            out.close()
                            del dict[lineconnid]


                #print(lineconnid,dstrtt1, dstrtt2,rttmin)

            #print(line) # already has newline
if __name__ == '__main__':
    main()
