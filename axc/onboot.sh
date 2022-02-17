#!/bin/sh
. /usr/local/bin/axcm/axc/axenv.sh
now=$(date +"%T")
echo "$now Insight Boot" >>/var/log/insight.log
echo "$now CustID $AXFCUSTID" >>/var/log/insight.log
echo "$now LoadMaster ID $AXFLMID" >>/var/log/insight.log
echo "$now LoadMaster IP $AXFLMIP" >>/var/log/insight.log
touch /var/log/$AXLMIP.log
tail -f /var/log/$AXFLMIP.log | sed -u -E "s/(.*) [a-zA-Z0-9_.-]* l7log: (.*?..*?..*?..*?:\w{1,5}): \((.*?..*?..*?..*?):\w{1,5}?.*(https|http):\/\/([a-zA-Z.]{0,253})(\/.*) \(User-Agent: (.*\))/\1,session,$AXFCUSTID,$AXFLMID,\3,\2,\5,\6,\"\7\"/gm;t;d" >>/var/log/session.log &
