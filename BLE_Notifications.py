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
    def __init__(self, name, MAC, sensors):
        self.name = name
        self.MAC = MAC
        self.sensors = sensors

def StartScan(duration):
    scanner = Scanner().withDelegate(SensorDelegate())
    devices = scanner.scan(duration)
    
    for dev in devices:
        if(dev.getValueText(0xFF)):
            if("4e4f4b" in dev.getValueText(0xFF)):

                sensor_array = bytearray.fromhex(dev.getValueText(0xFF))
                sensors_mounted = int(sensor_array[7])
                sensors_mounted += int(sensor_array[8] << 8)
                sensors_mounted += int(sensor_array[9] << 16)
                sensors_mounted += int(sensor_array[10] << 24)

                target = SensorModule(dev.getValueText(0x09), dev.addr, sensors_mounted)
                print "Battery module found, name = %s MAC: %s, sensors %d" % (target.name, target.MAC, target.sensors)
                return target

def SetTxLen(peripheral, tx_len):
    command = bytearray([0x42, 0x00, 0x00])
    command[1] = tx_len & 0x00FF
    command[2] = tx_len & 0xFF00
    peripheral.writeCharacteristic(0x15, command)

def SetSampleInterval(peripheral, interval):
    command = bytearray([0x49, 00, 00])
    command[1] = interval & 0x00FF
    command[2] = interval & 0xFF00
    peripheral.writeCharacteristic(0x15, '\x49\x00\x01')

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

def loopNotifications(peripheral, name, sensors):
    myString = ""
    time = os.popen("date")
    for c in time.readlines():
        myString += c

        myString = myString.rstrip()
    myFile.write(myString + '\n')
    myFile.write("Module name: %s\n" % (name))

    i = 0
    while (peripheral.waitForNotifications(0.5)):
        #peripheral.waitForNotifications(0.3)
        notification =  peripheral.delegate.readNotification()
        print notification.encode("hex")


        myFile.write(decodeData(notification.encode("hex"), sensors) + '\n')

        i += 1
    myFile.flush()

def decodeData(hexline, sensors_mounted):
    returnString = ""
    hex_array = bytearray.fromhex(hexline)
    seconds = int(hex_array[0] + (hex_array[1] << 8) + (hex_array[2] << 16) + (hex_array[3] << 24))
    returnString = "Time: %d\t" % (seconds)

    if(sensors_mounted & 0x01):
        temperature = float(hex_array[4] + (hex_array[5] << 8))
        returnString += "Temperature: %.1f\t" % (temperature/10.0)

    if(sensors_mounted & 0x02):
        humidity = float(hex_array[6] + (hex_array[7] << 8))
        returnString += "Humidity: %.1f%%\t" % (humidity/10.0)

    if(sensors_mounted & 0x0100):
        voltage = int(hex_array[4] + (hex_array[5] << 8))
        returnString += "Voltage: %d\t" % (voltage)

    if(sensors_mounted & 0x0400):
        temperature = float((hex_array[6] & 0x7F))  
        if(hex_array[7] & 0x80):
            temperature += 0.5
        returnString += "Temp: %.1f" % (temperature)
    #print "Time: %d\tVoltage: %d\tTemp: %.1f" % (seconds, voltage, temperature)
    return returnString

def main():
    global myFile
    myFile = open("SensorData_Streamed.txt", "a" )
    while(1):
        print "Scanning for Sensor Modules."
        target = StartScan(3)
        while (target is None):
            sys.stdout.write('.')
            sys.stdout.flush()
            target = StartScan(3)

        print "Target found, proceeding to connect!"
        try:
            #slave = Peripheral(target.MAC, "random")
            slave = Peripheral(target.MAC, "public")
       
            slave.setDelegate(SensorDelegate())
        except BTLEException, e:
            print "Connection failed!"
            print e.code
            print e.message
            time.sleep(3)
            continue

        discoverCharacteristics(slave)
        enableNotification(slave)

        loopNotifications(slave, target.name, target.sensors)
        SetTxLen(slave, 120)
        slave.disconnect()
        print "Disconnected"

main()
