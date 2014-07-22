#!/bin/bash
# A short script to lookup metrics in collectd via the collectd unix socket
# mjh 2014
TYPE=$1
METRIC=$2
SOCKET=$(grep -A4 unixsock /etc/collectd.conf| awk -F'"' '/SocketFile/ {print $2}')
THRESHOLD=$3
RESULT=$(printf '%.0f' $(collectdctl -s ${SOCKET} getval ${METRIC} | cut -d'=' -f2))

if [ $? -ne 0 ]; then
  echo -e "No data returned from collectd"
  exit 1
fi

case ${TYPE} in
HIGHER)
  if [ ${RESULT} -gt ${THRESHOLD} ]; then
    echo -e "Metric ${METRIC} has a value of ${RESULT} which is higher than threshold of ${THRESHOLD}"
    exit 1
  else
    echo -e "Metric ${METRIC} has a value of ${RESULT} which is ok"
    exit 0
  fi
  ;;
LOWER)
  if [ ${RESULT} -lt ${THRESHOLD} ]; then
    echo -e "Metric ${METRIC} has a value of ${RESULT} which is lower than threshold of ${THRESHOLD}"
    exit 1
  else
    echo -e "Metric ${METRIC} has a value of ${RESULT} which is ok"
    exit 0
  fi
  ;;
*)
  echo -e "Unknown error somwhere in system"
  exit 1
esac
