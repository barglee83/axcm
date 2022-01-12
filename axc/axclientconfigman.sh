#!/bin/bash
. /etc/profile.d/axenv.sh
# Basic if statement
if [ $AXFON == "Y" ]
then
echo $(date) >>/var/log/axf.log
/usr/local/bin/configman.py -i $AXFLMIP -u $AXFLMUSER -p $AXFLMPASS -c $AXFCUSTID -l $AXFLMID -x $AXFENDPOINT -o $AXFLMPORT -z $AXFEXECPATH -a $AXFAPIKEY >>/var/log/axf.log
fi