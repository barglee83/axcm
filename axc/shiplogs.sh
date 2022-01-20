#!/usr/bin/env bash
filename=l7-`date +%s`.log
cp /var/log/l7.log /var/log/$filename
echo "" >/var/log/l7.log
scp -i bgelk.pem /var/log/$filename azureuser@$SYSLOGENDPOINT:/home/azureuser/.
ssh -i bgelk.pem azureuser@$SYSLOGENDPOINT "cat $filename >>/var/log/elksession"