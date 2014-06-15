#!/usr/bin/python

# This is an example program showing how to use the BrickPi and Motor classes

import sys
sys.path.remove('/usr/local/lib/python2.7/dist-packages/BrickPi-0.0.0-py2.7.egg')
sys.path.remove('/usr/local/lib/python2.7/dist-packages/scratchpy-0.1.0-py2.7.egg')
import time
import pprint
import inspect
from BrickPi import *

#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(sys.path)

# setup the serial port for communication
# Enable the Motor B
mypi = BrickPi()
motorA = mypi.motors[PORT_A]
motorA.rotate(50, 360)

'''
for motor in mypi.motors():
    motor.enable()

BrickPiSetup()
BrickPi.MotorEnable[PORT_A] = 1
BrickPiSetupSensors()

#BrickPi.MotorSpeed[PORT_A] = 100
motorRotateDegree([90],[180],[PORT_A], 0.01)
BrickPiUpdateValues()
BrickPi.MotorSpeed[PORT_A] = 0
BrickPiUpdateValues()
'''
