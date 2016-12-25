#!/usr/bin/python

#This project aims to control a cheap Bluetooth RGBW-led controller through GATT writes.
#The service and characteristic UUID's are most likely different between manufacturers, but
#altering the code for a specific device should be trivial.

import sys
from bluepy.btle import Scanner, DefaultDelegate, Peripheral, BTLEException, Service
import time

class LedController:

    def __init__(self, name, MAC):
        self.name = name
        self.MAC = MAC
        self.device = Peripheral()
            #bytes representing colour brightness
        self.rgbw = bytearray([00, 00, 00, 00])

    def connect(self):
        self.device.connect(self.MAC, "public", None)

    def setColour(self, newColour):
        self.rgbw[0] = 0xFF & newColour
        self.device.writeCharacteristic(37, chr(self.rgbw[0]))
        self.rgbw[1] = 0xFF & (newColour >> 8)
        self.device.writeCharacteristic(40, chr(self.rgbw[1]))
        self.rgbw[2] = 0xFF & (newColour >> 16)
        self.device.writeCharacteristic(43, chr(self.rgbw[2]))
        self.rgbw[3] = 0xFF & (newColour >> 24)
        self.device.writeCharacteristic(49, chr(self.rgbw[3]))


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            #print "Discovered device", dev.addr
            return
        elif isNewData:
            #print "Received new data from", dev.addr
            return



def StartScan(duration):
    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(duration)

    for dev in devices:
            print "Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi)
            if( dev.getValueText(0x02) == "f0ffe5ffe0ff"  ):
                target = LedController(dev.getValueText(0x09), dev.addr)
                print "Led controller found, name: %s MAC: %s" % (target.name, target.MAC)
                return target

def DiscoverLedCharacteristics(peripheral):
    for service in peripheral.getServices():
        print service
        for characteristic in service.getCharacteristics():
            print characteristic

def main():
    print "Scanning for RGBW Led controllers..."
    target = StartScan(3)
    while (target is None):
        sys.stdout.write('.')
        sys.stdout.flush()
        target = StartScan(3)

    print "Target acquired, proceeding to connect to %s" % target.name
    try:
        target.connect()
    except BTLEException, e:
        print "Connection failed!"
        print e.code
        print e.message
        time.sleep(3)
        main()

    DiscoverLedCharacteristics(target.device)
    
    while(1):
        target.setColour(0x00000000)
        time.sleep(1)
        target.setColour(0xFFFFFFFF)
        time.sleep(1)

main()
