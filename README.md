# axcm

Files for gaining Telemtry Insights from LoadMaster

**Limitations**
* No Sub Vs Support
* Minimal Config Management




__Ax Client__
Procesing/Filtering of Syslog and Forwarding to AXM
Module to Create JSON rep of LoadMaster Metrics and Stats to be sent to AXM. Gathers info with RESTFUL API GETs and sends using POST
Config Sync. Queries AXM and updates config (Basic Functionality)

__Ax Manager__



**Centos 7 Install**
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
4. Install Dependencies

    ``sudo yum install epel-release``
    
    ``sudo yum install syslog-ng syslog-ng-libdbi``
    
    ``sudo yum install git``   
   
    ``sudo yum install python-pip``
    
    ``sudo pip install -r requirements.txt``
5. Enable Syslog-ng
    ```
    sudo systemctl stop rsyslog
    sudo systemctl disable rsyslog
    vi /etc/syslog-ng/syslog-ng.conf
    sudo systemctl start syslog-ng.service
    ```
    
6.
    Copy Files Using GIT
    git clone https://github.com/barglee83/axcm.git
    
```git clone https://github.com/barglee83/axcm.git
cp axcm/axc/*.py .
cp axcm/axc/*.sh .
chmod +x *.py *.sh 
cat axcm/axc/axfcron | sort -u | crontab -
 ```
    
 Firewall Updates
  

    firewall-cmd --permanent --zone=public --add-service=syslog
