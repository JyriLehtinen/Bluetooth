#!/usr/bin/python

#This code scans for BLE advertising and decodes sensor data from a certain type of sensor module prototype
import sys
from bluepy.btle import Scanner, DefaultDelegate, Peripheral, BTLEException, Service, Characteristic
import os 

import time

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

class SensorDelegate(DefaultDelegate):
    message = 0

    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        self.message = data

    def readNotification(self):
        return self.message

class SensorModule:
    def __init__(self, name, MAC):
        self.name = name
        self.MAC = MAC

def StartScan(duration):
    scanner = Scanner().withDelegate(SensorDelegate())
    devices = scanner.scan(duration)
    
    for dev in devices:
        if(dev.getValueText(0xFF)):
            if("4e4f4b" in dev.getValueText(0xFF)):
                target = SensorModule(dev.getValueText(0x09), dev.addr)
                print "Battery module found, name = %s MAC: %s" % (target.name, target.MAC)
                return target

def discoverCharacteristics(peripheral):
    for service in peripheral.getServices():
        print service
        service.getCharacteristics()


def enableNotification(peripheral):
    #this enables the voltage notifications
    peripheral.writeCharacteristic(0x0F, '\x01')


def disableNotification(peripheral):
    #this enables the voltage notifications
    peripheral.writeCharacteristic(0x0F, '\x00')

def loopNotifications(peripheral):
    peripheral.waitForNotifications(1.0)
    print str(peripheral.delegate.readNotification())

    loopNotifications(peripheral)

def main():
    global myFile
    myFile = open("ScannedData.txt", "a" )
    print "Scanning for Battery Modules."
    target = StartScan(3)
    while (target is None):
        sys.stdout.write('.')
        sys.stdout.flush()
        target = StartScan(3)

    print "Target found, proceeding to connect!"
    try:
        slave = Peripheral(target.MAC, "random")
        slave.setDelegate(SensorDelegate())
    except BTLEException, e:
        print "Connection failed!"
        print e.code
        print e.message
        return

    discoverCharacteristics(slave)
    enableNotification(slave)

    loopNotifications(slave)

main()
