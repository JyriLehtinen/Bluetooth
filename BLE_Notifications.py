#!/usr/bin/python

#This code scans for BLE advertising and decodes sensor data from a certain type of sensor module prototype
import sys
from bluepy.btle import Scanner, DefaultDelegate, Peripheral, BTLEException, Service, Characteristic
import os 

import time

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
        #Describes what sensors are mounted on the unit using a 4B bitfield
        self.sensors = sensors

def StartScan(duration):
    scanner = Scanner().withDelegate(SensorDelegate())
    devices = scanner.scan(duration)
    
    for dev in devices:
        if(dev.getValueText(0xFF)):
            if("4e4f4b" in dev.getValueText(0xFF)):
                #This means "NOK" was found in the advertising packet
                sensor_array = bytearray.fromhex(dev.getValueText(0xFF))
                #Populate the sensor bitfield according to the advertising packet
                sensors_mounted = int(sensor_array[7])
                sensors_mounted += int(sensor_array[8] << 8)
                sensors_mounted += int(sensor_array[9] << 16)
                sensors_mounted += int(sensor_array[10] << 24)

                target = SensorModule(dev.getValueText(0x09), dev.addr, sensors_mounted)
                print "Battery module found, name = %s MAC: %s, sensors %d" % (target.name, target.MAC, target.sensors)
                return target

#Changes the number of samples collected before transmitting them (default: 60) by writing 'B' followed by uint16_t in Little Endian
#Write is done to the configuration characteristic (Handle 0x15)
def SetTxLen(peripheral, tx_len):
    command = bytearray([0x42, 0x00, 0x00])
    command[1] = tx_len & 0x00FF
    command[2] = (tx_len & 0xFF00) >> 8
    peripheral.writeCharacteristic(0x15, command)

#This function changes the time between two samples (default: 1) by writing 'I' followed by uint16_t in Little Endian
def SetSampleInterval(peripheral, interval):
    command = bytearray([0x49, 00, 00])
    command[1] = interval & 0x00FF
    command[2] = (interval & 0xFF00) >> 8
    peripheral.writeCharacteristic(0x15, command) 

#This function populates the instance with GATT services and characteristics
def discoverCharacteristics(peripheral):
    for service in peripheral.getServices():
        print service
        service.getCharacteristics()


#Enable notifications in the data_stream characteristics by writing 0x01 to the descriptor (Handle 0x0F)
def enableNotification(peripheral):
    peripheral.writeCharacteristic(0x0F, '\x01')

#Disable the data_stream notifications 
def disableNotification(peripheral):
    peripheral.writeCharacteristic(0x0F, '\x00')

#Receive and save the data streamed by the sensor module
def loopNotifications(peripheral, name, sensors):
    myString = ""
    time = os.popen("date")
    for c in time.readlines():
        myString += c

        myString = myString.rstrip()
    myFile.write(myString + '\n')
    myFile.write("Module name: %s\n" % (name)) #Write the current date and time, along with the module name we're connected to

    i = 0
    while (peripheral.waitForNotifications(0.5)): #Keep looping until the wait times out (transmission over)
        notification =  peripheral.delegate.readNotification()
        print notification.encode("hex")


        myFile.write(decodeData(notification.encode("hex"), sensors) + '\n')

        i += 1
    myFile.flush()

#Decode the data streamed over BLE accordingly. How to interpret the data depends on the sensors mounted
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

def adjustConfigurations(slave, sensors):
    if(sensors & 0x03):
        SetTxLen(slave, 30)
        SetSampleInterval(slave, 10)
    elif(sensors & 0x0500):
        SetTxLen(slave, 240)
        SetSampleInterval(slave, 1)

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
        adjustConfigurations(slave, target.sensors)
        slave.disconnect()
        print "Disconnected"

main()
