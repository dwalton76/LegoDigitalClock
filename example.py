#!/usr/bin/python

# This is an example program showing how to use the BrickPi and Motor classes
import sys
sys.path.remove('/usr/local/lib/python2.7/dist-packages/BrickPi-0.0.0-py2.7.egg')
sys.path.remove('/usr/local/lib/python2.7/dist-packages/scratchpy-0.1.0-py2.7.egg')
from BrickPi import *

mypi = BrickPi()
motorA = mypi.motors[PORT_A]
logger.info("Initial Position: %d/%d" % (motorA.get_position_in_degrees(), motorA.position))

motorA.rotate(50, 180)
mypi.update_values()
motorA.update_position()
logger.info("Final   Position: %d/%d" % (motorA.get_position_in_degrees(), motorA.position))

