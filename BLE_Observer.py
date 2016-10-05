#!/usr/bin/python

#This code scans for BLE advertising and decodes sensor data from a certain type of sensor module prototype

from bluepy.btle import Scanner, DefaultDelegate

import os 

def getSensorData(device):
        ManufString = device.getValueText(0xFF)
        if("4e4f4b" in ManufString):
            myString = ""

            time = os.popen("date")
            for i in time.readlines():
                myString += i

                myString = myString.rstrip()

            sensor_array = bytearray.fromhex(ManufString)
            voltage = int(sensor_array[4] << 8)
            voltage += int(sensor_array[3])
            myString += ", " + str(voltage)

            if(sensor_array[5] == 0x2b):
                temp = float(sensor_array[6]/2.0)
            else:
                temp = float(-(sensor_array[6]/2.0))
            myString += ", " + str(temp)

            myString += ", %s" % device.getValueText(0x09)
            myString += "\n" 
            #print myString
            myFile.write(myString)
            StartScan(3)

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
            name = dev.getValueText(0x09)
            print "Name: %s" % name

            ManufString = dev.getValueText(0xFF)
            if("4e4f4b" in ManufString):
                myString = ""

                time = os.popen("date")
                for i in time.readlines():
                    myString += i
                    myString = myString.rstrip()

                sensor_array = bytearray.fromhex(ManufString)
                voltage = int(sensor_array[4] << 8)
                voltage += int(sensor_array[3])
                myString += ", " + str(voltage)

                if(sensor_array[5] == 0x2b):
                    temp = float(sensor_array[6]/2.0)
                else:
                    temp = float(-(sensor_array[6]/2.0))
                myString += ", " + str(temp)

                myString += ", %s" % name
                myString += "\n" 
                #print myString
                myFile.write(myString)

    StartScan(duration)


def main():
    global myFile
    myFile = open("ScannedData.txt", "a" )
    timeout = input("Enter the scan duration in seconds: ")
    StartScan(timeout)

main()

