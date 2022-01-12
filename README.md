
# AXCM

Software for gaining Telemetry Insights from LoadMaster, Generating Events and Syncing Config

##Overview

#### Limitations
* No Sub Vs Support
* Minimal Config Management

#### Requirements
LoadMaster
AXC deployed with LoadMaster Creds (user/pass etc)
AXM Running. This can be using 
1. Cloud Version dev.ax.barglee.com with apikey and custid 
2. Locally Run - Custid is 443. No APIKEY Reqd.


## Ax Client

##### Continuous Procesing/Filtering of Syslog and Forwarding to AXM
This is done with two different commands:

`python /usr/local/bin/parseL7.py -c 1001 -l 1`
- This Writes Logs to l7.log file

`tail -f /var/log/LoadMaster.log | sed -u -E "s/(.*) [a-zA-Z0-9_.-]* l7log: (.*?..*?..*?..*?:\w{1,5}): \((.*?..*?..*?..*?):\w{1,5}?.*(https|http):\/\/([a-zA-Z.]{0,253})(\/.*) \(User-Agent: (.*\))/\1,session,$AXFCUSTID,$AXFLMID,\3,\2,\5,\6,\"\7\"/gm;t;d" >>/var/log/session.log &`
- This writes Logs to session.log

Our Syslog config Will then Send this data to configured Syslog Server (AXM Endpoint)
```
source sessions {
    file("/var/log/session.log" follow-freq(1) flags(no-parse));
};
source l7 {
    file("/var/log/l7.log" follow-freq(1) flags(no-parse));
};
---
destination d_syslog_udp { syslog("20.123.188.121" transport("udp") port(514)); };
---
log { source(l7); destination(d_syslog_udp);};
log { source(sessions); destination(d_syslog_udp);};
```

`/usr/local/bin/logprocessing.sh` Is the Shell Script that can be Started on Boot through `/etc/systemd/system/sample.service`


##### Reporting of Stats
Module to Create JSON rep of LoadMaster Metrics and Stats to be sent to AXM
Gathers info with RESTFUL API GETs and sends using POST

##### Configuration Sync
Config Sync. Queries AXM and updates config (Basic Functionality)

## Ax Manager
* Influx
* Logstash
* Elasticsearch
* Kibana
* go Program for processing stats and serving config.

##### Receives Stats - writes to Influx, Runs Issue checks
`parsejsonpost.go`
- XXXXX Needs an option to disable influx write

##### Receivs Config Query and serves
exmaple config 
`lmconfig_0000_0000.json`

Receives formatted syslog - processed by logstash

 **/var/log/elksession**
 
 **/var/log/events.log**

`example.conf`

(Note on restart these get reloaded.)

Runs kibana and influx UIs

___

##Build

###AXC
**Centos 7 Install**

##### Initial setup
1. Configure Ip Address Settings
    ``vi /etc/sysconfig/network-scripts/ifcfg-ens192``
    ```
    BOOTPROTO static
    ONBOOT yes    
    IPADDR    
    NETMASK    
    GATEWAY
    ```
2. Restart NIC ``service network restart``
3. Add DNS Server ``vi /etc/resolv.conf``
    ```nameserver 8.8.8.8```

##### Requirements 


 
5. Install Dependencies

    ``sudo yum install epel-release``
    
    ``sudo yum install syslog-ng syslog-ng-libdbi``
    
    ``sudo yum install git``   
   
    ``sudo yum install python-pip``
    
    
    
1. Navigate to Directory:
`cd /usr/local/bin`
    
2.  Copy Files Using GIT
 
       
```
git clone https://github.com/barglee83/axcm.git
cp axcm/axc/*.py .
cp axcm/axc/*.sh .
chmod +x *.py *.sh 
cat axcm/axc/axfcron | sort -u | crontab -
 ```
 
 3. Install Python Requirements
 ``sudo pip install -r axcm/axc/requirements.txt``

4. set environment Variables:

cd /etc/profile.d/
vi axenv.sh

```
AXFON=Y
AXFLMIP=10.0.0.7
AXFLMPASS=su5PavUc
AXFLMID=1
AXFAPIKEY=f3c71128-0263-45e0-82cf-3b7afc281ddf
AXFENDPOINT=dev.ax.barglee.com
AXFCUSTID=1001
AXFLMUSER=bal
AXFEXECPATH=/usr/local/bin/
AXFWAIT=5
AXFLMPORT=8443

```

`chmod 755 /etc/profile.d/axenv.sh`
 
3. Enable Syslog-ng
    ```
    sudo systemctl stop rsyslog
    sudo systemctl disable rsyslog
    vi /etc/syslog-ng/syslog-ng.conf
    sudo systemctl start syslog-ng.service
    ```

 
    
4. Firewall Updates
  

    firewall-cmd --permanent --zone=public --add-service=syslog

5. Execute Tail commands

6. Define Scripts to start on boot


###AXM

####AXM FrontEnd
LoadMaster with the following:
Influx, kibana, dev all behind https

Influx Kibana Requires Auth via barglee domain for admin access
(Influx has extra pw check axfuser:....)

API Key Required for 'DEV'
Custid in URL routes to correct RS.
Single Process/Port per Customer.

##Startup
###AXC

###AXM
```
docker ps -a
docker start 2fb115b249dd
docker start 5902a2b5d426
docker start 92bea6f35c0d
/usr/share/logstash/bin/logstash -f example.conf
  
cd /usr/local/bin
go run parsejsonpost.go 1001

```

###Other
Test LM & RSs
```
sudo ./multiWWW.sh 
```