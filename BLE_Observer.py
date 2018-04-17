#!/usr/bin/python

#This code scans for BLE advertising and decodes sensor data from a certain type of sensor module prototype

from bluepy.btle import Scanner, DefaultDelegate

import os 

def getVikingData(device):
        FrameString = device.getValueText(0x16)
        print ""
        print "Device: %s, RSSI: %d dBm" % (device.addr, device.rssi)
        print FrameString
        FrameArray = bytearray.fromhex(FrameString)

        if(FrameArray[2] == 0x80):
            print "Viking data!"
            myString = ""

            time = os.popen("date")
            for i in time.readlines():
                myString += i

                myString = myString.rstrip()

            acc_rms = int(FrameArray[17] << 8)
            acc_rms += int(FrameArray[16])
            myString += ", " + str(acc_rms)

            myString += ", %s" % device.addr
            myString += "\n" 
            #print myString
            myFile.write(myString)

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

#def handleDiscovery(self, dev, isNewDev, isNewData):
#if isNewDev:
#print "Discovered device", dev.addr
#elif isNewData:
#print "Received new data from", dev.addr



def StartScan(duration):
    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(duration)

    for dev in devices:
#print "Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi)
#try:
#name = dev.getValueText(0x09)
#print "Name: %s" % name
#except:
#print "No name sent"

            if(dev.getValueText(0x03) == "aafe"):
                getVikingData(dev)

    StartScan(duration)


def main():
    global myFile
    myFile = open("ScannedData.txt", "a" )
    timeout = input("Enter the scan duration in seconds: ")
    StartScan(timeout)

main()

