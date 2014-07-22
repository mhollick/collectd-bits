#!/usr/bin/python
"""
Short script to restart a service when told to by collectd and log results.
test like:

cat 'Severity: FAILURE
Time: 1405504332.713
Host: collectd.vbox
Plugin: flume
Type: gauge
TypeInstance: CHANNEL
DataSource: value
CurrentValue: 6.000000e+01
WarningMin: nan
WarningMax: 1.000000e+01
FailureMin: nan
FailureMax: 5.000000e+01

Host collectd.vbox, plugin flume type gauge (instance CHANNEL): Data source "value" is currently 60.000000. That is above the failure threshold of 50.000000.
' | ./collectd-restart-service.py

mjh 20140717
"""

import sys
import os
import subprocess
import syslog
import socket

def collectd_in():
    """
    Pull in collectd event from stdin.
    Keep the plugin value
    Keep the message
    drop everything else
    """
    for line in sys.stdin:
        if line.startswith("Plugin:"):
            a,service = line.split(' ', 1)
    return service.strip(), line.strip()

def alert_to_statsd(result, service):
    """
    Send a metric to graphite as an event via the local statsd service.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if result == 0:
        message = "events.{0}.restart.success:1|c".format(service)
    else:
        message = "events.{0}.restart.fail:1|c".format(service)
    sock.sendto(message, ("127.0.0.1", 8125))

def alert_to_cloudwatch():
    """
    Send an alert to Cloudwatch (tm).
    """
    pass

def alert_to_syslog(result, service, message):
    """
    Keep syslog uptodate.
    """
    syslog.openlog("collectd", 0, syslog.LOG_DAEMON)
    if result != 0:
        syslog.syslog(syslog.LOG_ERR,
            "Collectd has failed to restart service: \"{0}\" collectd message was: \"{1}\"".
            format(service, message))
    elif result == -1:
        syslog.syslog(syslog.LOG_ERR,
            "Collectd attempted to restart unknown service: \"{0}\" collectd message was: \"{1}\"".
            format(service, message))
    else:
        syslog.syslog(syslog.LOG_WARNING,
            "Collectd has restarted service: \"{0}\" collectd message was: \"{1}\"".
            format(service, message))
    syslog.closelog()

def main():
    """
    check if service to be restated is valid
    try to restart it
    alert to statsd
    alert to syslog
    """
    service, message = collectd_in()
    services = next(os.walk("/etc/init.d"))[2]
    if service in services:
        init_script = "/etc/init.d/" + service
        result = subprocess.check_call([init_script, "restart"])
    else:
        result = -1
    alert_to_statsd(result, service)
    alert_to_syslog(result, service, message)


if __name__ == "__main__":
    """
    Make it so, number one.
    """
    main()
