#!/usr/bin/python

import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
for port in ports:
    if "RAMBo" in port[1] or "VID:PID=27b1:0001" in port[2]:
        snr = port[2].find("SNR=")
        if snr >= 0:
            snr = port[2][snr+4:]
        print "Found RAMBo board %s with serial : %s" % (port[0], snr)
