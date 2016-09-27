#!/usr/bin/python

#This project aims to control a cheap Bluetooth RGBW-led controller through GATT writes.
#The service and characteristic UUID's are most likely different between manufacturers, but
#altering the code for a specific device should be trivial.

import sys
from bluepy.btle import Scanner, DefaultDelegate, Peripheral, BTLEException, Service

def getSensorData(device):
        ManufString = device.getValueText(0xFF)
        if("4e4f4b" in ManufString):
            sensor_array = bytearray.fromhex(ManufString)
            voltage = int(sensor_array[4] << 8)
            voltage += int(sensor_array[3])
            print voltage

            if(sensor_array[5] == 0x2b):
                temp = float(sensor_array[6]/2)
            else:
                temp = float(-(sensor_array[6]/2))
            print temp

class LedController:
    #bytes representing colour brightness
    red = 0x00
    green = 0x00
    blue = 0x00
    white = 0x00

    #32 bit number to describe all colours in same variable
    rgbw = 0x00000000

    def __init__(self, name, MAC):
        self.name = name
        self.MAC = MAC


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
    peripheral.getServices()
    print peripheral.services

def main():
    print "Scanning for RGBW Led controllers..."
    target = StartScan(3)
    while (target is None):
        sys.stdout.write('.')
        sys.stdout.flush()
        target = StartScan(3)

    print "Target acquired, proceeding to connect to %s" % target.name
    try:
        slave = Peripheral(target.MAC)
    except BTLEException:
        print "Connection failed!"

    DiscoverLedCharacteristics(slave)

main()
