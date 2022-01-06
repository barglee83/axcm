# AXCM

Files for gaining Telemtry Insights from LoadMaster

##Overview

#### Limitations
* No Sub Vs Support
* Minimal Config Management




#### Ax Client

Procesing/Filtering of Syslog and Forwarding to AXM

Module to Create JSON rep of LoadMaster Metrics and Stats to be sent to AXM. 

Gathers info with RESTFUL API GETs and sends using POST

Config Sync. Queries AXM and updates config (Basic Functionality)

#### Ax Manager

Receives Stats - writes to Influx, Runs Issue checks

Receives formatted syslog - processed by logstash

Runs kibanan and influx UIs
___

##AXC
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
    
    ``sudo pip install -r requirements.txt``
    
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

6. Define Variables in env
