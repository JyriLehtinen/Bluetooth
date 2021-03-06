#!/usr/bin/python

from bluepy.btle import Scanner, DefaultDelegate

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print "Discovered device", dev.addr
        elif isNewData:
            print "Received new data from", dev.addr



def StartScan(duration):
    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(duration)

    for dev in devices:
            print "Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi)
            for (adtype, desc, value) in dev.getScanData():
                print " %s = %s" % (desc, value)
def main():
    print("This program will scan for user user defined duration. This process will loop until process is interrupted e.g. with CTRL+C")
    timeout = input("Enter the scan duration in seconds: ")
    while(1):
	    StartScan(timeout)

main()
