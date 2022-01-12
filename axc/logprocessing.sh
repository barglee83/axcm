#!/bin/bash
. /etc/profile.d/axenv.sh
touch /var/log/LoadMaster.log
tail -f /var/log/LoadMaster.log | sed -u -E "s/(.*) [a-zA-Z0-9_.-]* l7log: (.*?..*?..*?..*?:\w{1,5}): \((.*?..*?..*?..*?):\w{1,5}?.*(https|http):\/\/([a-zA-Z.]{0,253})(\/.*) \(User-Agent: (.*\))/\1,session,$AXFCUSTID,$AXFLMID,\3,\2,\5,\6,\"\7\"/gm;t;d" >>/var/log/session.log &
python /usr/local/bin/parseL7.py -c $AXFCUSTID -l $AXFLMID -i /var/log/LoadMaster.log -o /var/log/l7.log>>/var/log/axf.log