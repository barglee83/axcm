
# Project Insight

Software for gaining Telemetry Insights from LoadMaster, Generating Events and Syncing Config

##Overview

#### Limitations
* No Sub Vs Support
* Minimal Config Management

#### Requirements
LoadMaster
> Syslog Pointed at AXC
> ESP on with Delegate to Server
> Disable Local Extended ESP Logs
> Enable System Debug ad on Vs enable Full Debug+ HTTP Headers

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

e.g.
```[Unit]
Description=Description for sample script goes here
After=network.target

[Service]
Type=idle
ExecStart=/usr/local/bin/logprocessing.sh

TimeoutStartSec=0

[Install]
WantedBy=default.target
```

Environment Variables hee: /etc/profile.d/axf.sh 




/etc/profile.d/axenv.sh is where Global Variables are stored


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
AXFLMPASS=XXXXX
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
       
    ``sudo yum install golang``
    
    
    
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
 
Logstash Grok:

Reference: https://github.com/elastic/logstash/blob/v1.4.0/patterns/grok-patterns

Pattern Exmaples:
1. ESP User Logs
2. L7 Logs
3. 

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

Traffic Generation:
------------------

curl  https://mail.barglee.com

curl --tlsv1.2 --tls-max 1.2 -H "User-Agent: xx" url

Firefox:
curl --tlsv1.2 --tls-max 1.2 -H "User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0" https://mail.barglee.com/BADPATH2

Safari:
curl --tlsv1.2 --tls-max 1.2 -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Safari/605.1.15" https://mail.barglee.com/

Edge:
curl --tlsv1.2 --tls-max 1.2 -H "User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4811.0 Safari/537.36 Edg/99.0.1131.3" https://mail.barglee.com/

Opera:
curl --tlsv1.2 --tls-max 1.2 -H "User-Agent: Opera/9.80 (Android; Opera Mini/62.1.2254/191.256; U; pl) Presto/2.12.423 Version/12.16" https://mail.barglee.com/

Android:
curl --tlsv1.2 --tls-max 1.2 -H "User-Agent: Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19" https://mail.barglee.com/

chrome:
curl --tlsv1.2 --tls-max 1.2 -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36" https://mail.barglee.com/



curl --tlsv1.2 --tls-max 1.2 -H "User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0" https://mail.barglee.com/BADPATH2 --insecure
curl --tlsv1.2 --tls-max 1.2 -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Safari/605.1.15" https://mail.barglee.com/ --insecure
curl --tlsv1.2 --tls-max 1.2 -H "User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4811.0 Safari/537.36 Edg/99.0.1131.3" https://mail.barglee.com/ --insecure
curl --tlsv1.2 --tls-max 1.2 -H "User-Agent: Opera/9.80 (Android; Opera Mini/62.1.2254/191.256; U; pl) Presto/2.12.423 Version/12.16" https://mail.barglee.com/ --insecure
curl --tlsv1.2 --tls-max 1.2 -H "User-Agent: Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19" https://mail.barglee.com/ --insecure
curl --tlsv1.2 --tls-max 1.2 -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36" https://mail.barglee.com/ --insecure


