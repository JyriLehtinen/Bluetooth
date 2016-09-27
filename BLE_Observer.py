#!/usr/bin/python

#This code scans for BLE advertising and decodes sensor data from a certain type of sensor module prototype

from bluepy.btle import Scanner, DefaultDelegate

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
            getSensorData(dev)

def main():
    timeout = input("Enter the scan duration in seconds: ")
    StartScan(timeout)

main()

