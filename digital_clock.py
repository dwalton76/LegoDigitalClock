#!/usr/bin/python

import threading
import re
import sys
sys.path.remove('/usr/local/lib/python2.7/dist-packages/BrickPi-0.0.0-py2.7.egg')
sys.path.remove('/usr/local/lib/python2.7/dist-packages/scratchpy-0.1.0-py2.7.egg')
from BrickPi import *
from time import sleep
import datetime


turns = range(10)
turns[0] = range(10)
turns[0][0] = None
turns[0][1] = (-5, 7, -5, 3, -1)
turns[0][2] = (4, -6, 2)
turns[0][3] = (-4, 6, -4, 2)
turns[0][4] = (7, -7, 6, -3, 2)
turns[0][5] = (-4, 6, -2)
turns[0][6] = (-2, 4)
turns[0][7] = (-5, 7, -5, 3)
turns[0][8] = (2, 3, 1)
turns[0][9] = (-5, 7, -3, 1)

turns[1] = range(10)
turns[1][0] = (5, -7, 6, -4, 1)
turns[1][1] = None
turns[1][2] = (5, -6, 2)
turns[1][3] = (5, -8, 6, -4, 2)
turns[1][4] = (3, -3, 2)
turns[1][5] = (5, -8, 6, -2)
turns[1][6] = (5, -7, 5)
turns[1][7] = (1)
turns[1][8] = (5, -7, 5, -2)
turns[1][9] = (3, -3, 1)

turns[2] = range(10)
turns[2][0] = (-3, 6, -4, 1)
turns[2][1] = (-5, 7, -5, 3, -1)
turns[2][2] = None
turns[2][3] = (-4, 6, -4, 2)
turns[2][4] = (-5, 7, -3, 2)
turns[2][5] = (-4, 6, -2)
turns[2][6] = (-3, 5)
turns[2][7] = (-5, 7, -5, 3)
turns[2][8] = (-3, 5, -3, 1)
turns[2][9] = (-5, 7, -3, 1)

turns[3] = range(10)
turns[3][0] = (3, -4, 1)
turns[3][1] = (-5, 7, -5, 3, -1)
turns[3][2] = (4, 6, 2)
turns[3][3] = None
turns[3][4] = (-5, 7, -3, 2)
turns[3][5] = (4, -6, 4)
turns[3][6] = (3, -5, 4)
turns[3][7] = (-5, 7, -5, 3)
turns[3][8] = (3, -5, 3, -1)
turns[3][9] = (-5, 7, -3, 1)

turns[4] = range(10)
turns[4][0] = (3, -7, 6, -4, 1)
turns[4][1] = (-4, 3, -1)
turns[4][2] = (3, -6, 2)
turns[4][3] = (3, -8, 6, -4, 2)
turns[4][4] = None
turns[4][5] = (-9, 6, -2) # double check this one
turns[4][6] = (3, -7, 5)
turns[4][7] = (-4, 3)
turns[4][8] = (3, -7, 5, -3, 1)
turns[4][9] = (-1)

turns[5] = range(10)
turns[5][0] = (3, -4, 1)
turns[5][1] = (-5, 7, -5, 3, -1)
turns[5][2] = (4, -6, 2)
turns[5][3] = (-2, 2)
turns[5][4] = (-5, 7, -3, 2)
turns[5][5] = None
turns[5][6] = (3, -5, 4)
turns[5][7] = (-5, 7, -5, 3)
turns[5][8] = (3, -5, 3, -1)
turns[5][9] = (-5, 7, -3, 1)

turns[6] = range(10)
turns[6][0] = (1, -4, 1)
turns[6][1] = (-7, 7, -5, 3, -1)
turns[6][2] = (2, -6, 2)
turns[6][3] = (-6, 6, -4, 2)
turns[6][4] = (-7, 7, -3, 2)
turns[6][5] = (-6, 6, -2)
turns[6][6] = None
turns[6][7] = (-7, 7, -5, 3)
turns[6][8] = (-3, 1)
turns[6][9] = (-7, 7, -3, 1)

turns[7] = range(10)
turns[7][0] = (4, -7, 6, -4, 1)
turns[7][1] = (-1)
turns[7][2] = (4, -6, 2)
turns[7][3] = (4, -8, 6, -4, 2)
turns[7][4] = (2, -3, 2)
turns[7][5] = (4, -8, 6, -2)
turns[7][6] = (4, -7, 5)
turns[7][7] = None
turns[7][8] = (4, -7, 5, -3, 1)
turns[7][9] = (2, -3, 1)

turns[8] = range(10)
turns[8][0] = (3, -4, 1)
turns[8][1] = (-5, 7, -5, 3, -1)
turns[8][2] = (4, -6, 2)
turns[8][3] = (-4, 6, -4, 2)
turns[8][4] = (-5, 7, -3, 2)
turns[8][5] = (-4, 6, -2) # check this one
turns[8][6] = (2)
turns[8][7] = (-5, 7, -5, 3)
turns[8][8] = None
turns[8][9] = (7, -7, 6, -3, 1)

turns[9] = range(10)
turns[9][0] = (4, -7, 6, -4, 1)
turns[9][1] = (-3, 3, -1)
turns[9][2] = (4, -6, 2)
turns[9][3] = (4, -8, 6, -4, 2)
turns[9][4] = (1)
turns[9][5] = (4, -8, 6, -2)
turns[9][6] = (4, -7, 5)
turns[9][7] = (-3, 3)
turns[9][8] = (4, -7, 5, -3, 1)
turns[9][9] = None

class LegoClock(BrickPi):
    def __init__(self):
        BrickPi.__init__(self)
        self.digits = []
        self.digit1 = self.motors[PORT_D]
        self.digit2 = self.motors[PORT_C]
        self.digit3 = self.motors[PORT_B]
        self.digit4 = self.motors[PORT_A]

    # We keep track of the last known position of each digit
    def load_state(self):
        fh = open('digital_clock.state', 'r')
        line = fh.readlines()[0]
        fh.close()
        result = re.search('(\d)(\d):(\d)(\d)', line)
        self.digit1.current  = int(result.group(1))
        self.digit2.current  = int(result.group(2))
        self.digit3.current  = int(result.group(3))
        self.digit4.current  = int(result.group(4))

    def save_state(self):
        fh = open('digital_clock.state', 'w')
        fh.write('%d%d:%d%d\n' % (self.digit1.current, self.digit2.current, self.digit3.current, self.digit4.current))
        fh.close()

    def set_targets(self, use_military_time):
        now = datetime.datetime.now()
        hour = now.hour

        if not hour:
            hour = 12
        elif not use_military_time and hour > 12:
            hour -= 12

        hh_mm = "%02d:%02d" % (hour, now.minute)
        logger.info('SET: %s' % hh_mm)
        result = re.search('(\d)(\d):(\d)(\d)', hh_mm)
        self.digit1.target = int(result.group(1))
        self.digit2.target = int(result.group(2))
        self.digit3.target = int(result.group(3))
        self.digit4.target = int(result.group(4))

    def move_digit(self, digit):
        if digit.current == digit.target:
            return

        logger.info('%s: %d -> %d via %s' % (digit, digit.current, digit.target, turns[digit.current][digit.target]))

        # About turns[]
        # - the numbers indicate the number of 90 degree turns of the top component
        # - a positive number means turn it clockwise, negative counter clockwise
        #
        # I am using a 1:3 ratio so to turn the top part 90 degrees I need to rotate the motor 270 degrees.
        # FYI this is a nice page for calculating what gear ratio you are using:
        # http://gears.sariel.pl/
        #
        # I am using a power of 80
        for x in turns[digit.current][digit.target]:
            digit.rotate(80, 270 * -x)
        digit.current = digit.target

    def move_digits(self):

        self.move_digit(self.digit4)
        self.move_digit(self.digit3)
        self.move_digit(self.digit2)
        self.move_digit(self.digit1)
        # dwalton
        return

        # Enable this once it is thread safe
        '''
        # Must change all 4 digits
        if (self.digit1.current != self.digit1.target and
            self.digit2.current != self.digit2.target and
            self.digit3.current != self.digit3.target and
            self.digit4.current != self.digit4.target):
            logger.info('move_digits: change 4 digits')

            self.digit2.start()
            self.digit4.start()
            self.digit2.join()
            self.digit4.join()

            self.digit1.start()
            self.digit3.start()
            self.digit1.join()
            self.digit3.join()

        # Must change 3 digits
        elif (self.digit2.current != self.digit2.target and
              self.digit3.current != self.digit3.target and
              self.digit4.current != self.digit4.target):
            logger.info('move_digits: change 3 digits')
            self.digit2.start()
            self.digit4.start()
            self.digit2.join()
            self.digit4.join()

            self.digit3.start()
            self.digit3.join()

        # Must change 2 digits
        elif (self.digit3.current != self.digit3.target and
              self.digit4.current != self.digit4.target):
            logger.info('move_digits: change 2 digits')
            self.digit3.start()
            self.digit3.join()
            self.digit4.start()
            self.digit4.join()

        # Only update the minute
        elif self.digit4.current != self.digit4.target:
            logger.info('move_digits: change 1 digit')
            self.digit4.start()
            self.digit4.join()
        '''

if __name__ == '__main__':
    myclock = LegoClock()
    myclock.load_state()

    while (True):
        myclock.set_targets(False)
        myclock.move_digits()
        myclock.save_state()
        now = datetime.datetime.now()
        logger.info('sleeping for: %d' % (60 - now.second + 1))
        sleep(60 - now.second + 1)

