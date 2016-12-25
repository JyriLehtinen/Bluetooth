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
        red = newColour & 0xFF
        green = (newColour >> 8) & 0xFF
        blue = (newColour >> 16) & 0xFF
        white = (newColour >> 24) & 0xFF

        if(~(self.rgbw[0] & red)):
            self.rgbw[0] = red
            self.device.writeCharacteristic(37, chr(self.rgbw[0]))
        if(~(self.rgbw[1] & green)):
            self.rgbw[1] = green
            self.device.writeCharacteristic(40, chr(self.rgbw[1]))
        if(~(self.rgbw[2] & blue)):
            self.rgbw[2] = blue
            self.device.writeCharacteristic(43, chr(self.rgbw[2]))
        if(~(self.rgbw[3] & white)):
            self.rgbw[3] = white
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
        #print service
        i=0
        for characteristic in service.getCharacteristics():
            #print characteristic
            i=0

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

    colour = 0x000000FF
    while(1):
        target.setColour(colour & 0xFFFFFF)
        time.sleep(0.1)
        colour *= 2
        if(colour == 0x01FE0000):
            colour = 0x01FE0001
        if(colour == 0x03FC0002):
            colour = 0x03FC0003
        if(colour == 0x07F80006):
            colour = 0x07F80007
        if(colour == 0x0FF0000E):
            colour = 0x0FF0000F

        if(colour == 0x1FE0001E):
            colour = 0x1FE0001F
        if(colour == 0x3FC0003E):
            colour = 0x3FC0003F
        if(colour == 0x7F80007E):
            colour = 0x7F80007F
        if(colour == 0xFF0000FE):
            colour = 0x000000FF

main()
