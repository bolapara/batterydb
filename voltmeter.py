from time import sleep
from UUGear import *
from sys import exit

CORRECTION = 0.025
DEVICE = 'UUGear-Arduino-4694-3532'


print "Correction value is %f" % CORRECTION

def open():
    global device
    UUGearDevice.setShowLogs(0)
    device = UUGearDevice(DEVICE)
    if not device.isValid():
        device.detach()
        device.stopDaemon()
        device = UUGearDevice(DEVICE)
    if not device.isValid():
        print 'UUGear device is not correctly initialized.'

def close():
    device.detach()
    device.stopDaemon()

def sample(samples):
    total = 0.0
    for _ in range(samples):
        total += device.analogRead(3)
        sleep(0.05)
    return (((total * 5) / 1024) / samples) + CORRECTION
