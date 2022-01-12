#!/bin/bash
. /etc/profile.d/axenv.sh
if [ $AXFON == "Y" ]
then
echo $(date)>>/var/log/axf.log
/usr/local/bin/reportStats.py -i $AXFLMIP -u $AXFLMUSER -p $AXFLMPASS -c $AXFCUSTID -l $AXFLMID -x $AXFENDPOINT -o $AXFLMPORT  -a $AXFAPIKEY>>/var/log/axf.log
fi