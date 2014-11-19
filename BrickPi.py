
#
# Credit for the original source here goes to:
# https://github.com/DexterInd/BrickPi_Python/blob/master/BrickPi.py
#
# It has been modified to make more use of classes.
import time
import serial
import logging

#logging.basicConfig(level=logging.DEBUG,
logging.basicConfig(filename='/var/log/brickpi.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)5s %(module)13s: %(message)s')
logger = logging.getLogger(__name__)

PORT_A = 0
PORT_B = 1
PORT_C = 2
PORT_D = 3

PORT_1 = 0
PORT_2 = 1
PORT_3 = 2
PORT_4 = 3

# The I2C speed (see below) for the ultrasound is hard
# coded to 7 in the firmware of the BrickPi. Unfortunately
# this speed is not very robust and sometimes causes the
# most significant bit to become corrupted. This leads to
# values being wrong by +-128.

# This modification to BrickPi.py fixes the problem
# without changing any program source code by mapping
# TYPE_SENSOR_ULTRASONIC_CONT to TYPE_SENSOR_I2C and
# setting it up manually.

# For more info see the BrickPi forum:
# http://www.dexterindustries.com/forum/?topic=problem-ultrasonic-sensor/#post-1273

# If you still have problems try tweaking the value below

US_I2C_SPEED = 10 #tweak this value
US_I2C_IDX = 0
LEGO_US_I2C_ADDR = 0x02
LEGO_US_I2C_DATA_REG = 0x42
#######################

MASK_D0_M = 0x01
MASK_D1_M = 0x02
MASK_9V   = 0x04
MASK_D0_S = 0x08
MASK_D1_S = 0x10

BYTE_MSG_TYPE              = 0 # MSG_TYPE is the first byte.
MSG_TYPE_CHANGE_ADDR       = 1 # Change the UART address.
MSG_TYPE_SENSOR_TYPE       = 2 # Change/set the sensor type.
MSG_TYPE_VALUES            = 3 # Set the motor speed and direction, and return the sensors and encoders.
MSG_TYPE_E_STOP            = 4 # Float motors immidately
MSG_TYPE_TIMEOUT_SETTINGS  = 5 # Set the timeout
# New UART address (MSG_TYPE_CHANGE_ADDR)
BYTE_NEW_ADDRESS   = 1

# Sensor setup (MSG_TYPE_SENSOR_TYPE)
BYTE_SENSOR_1_TYPE = 1
BYTE_SENSOR_2_TYPE = 2

BYTE_TIMEOUT=1

TYPE_MOTOR_PWM               = 0
TYPE_MOTOR_SPEED             = 1
TYPE_MOTOR_POSITION          = 2

TYPE_SENSOR_RAW              = 0 # - 31
TYPE_SENSOR_LIGHT_OFF        = 0
TYPE_SENSOR_LIGHT_ON         = (MASK_D0_M | MASK_D0_S)
TYPE_SENSOR_TOUCH            = 32
TYPE_SENSOR_ULTRASONIC_CONT  = 33
TYPE_SENSOR_ULTRASONIC_SS    = 34
TYPE_SENSOR_RCX_LIGHT        = 35 # tested minimally
TYPE_SENSOR_COLOR_FULL       = 36
TYPE_SENSOR_COLOR_RED        = 37
TYPE_SENSOR_COLOR_GREEN      = 38
TYPE_SENSOR_COLOR_BLUE       = 39
TYPE_SENSOR_COLOR_NONE       = 40
TYPE_SENSOR_I2C              = 41
TYPE_SENSOR_I2C_9V           = 42

BIT_I2C_MID  = 0x01  # Do one of those funny clock pulses between writing and reading. defined for each device.
BIT_I2C_SAME = 0x02  # The transmit data, and the number of bytes to read and write isn't going to change. defined for each device.

INDEX_RED   = 0
INDEX_GREEN = 1
INDEX_BLUE  = 2
INDEX_BLANK = 3

class Motor():
    def __init__(self, brickpi, port):
        self.brickpi = brickpi
        self.port = port

        if self.port == PORT_A:
            self.name = "A"
        elif self.port == PORT_B:
            self.name = "B"
        elif self.port == PORT_C:
            self.name = "C"
        elif self.port == PORT_D:
            self.name = "D"

        self.power = 0
        self.speed = 0
        self.position = 0
        self.enabled = 0

    def __str__(self):
        return self.name

    def update_position(self):
        self.position = self.brickpi.Encoder[self.port]

    def get_position_in_degrees(self):
        return (self.position % 720)/2

    def stop(self, brake):

        if brake:
            #logger.debug("Motor %s: applying brakes" % self)

            # Run the motors in reverse direction to stop instantly
            self.speed =  -1 * self.speed

            self.brickpi.update_values()
            time.sleep(.04) # 40ms initially

        #logger.debug("Motor %s: stopping" % self)
        self.enabled = 0
        self.brickpi.update_values()

    # Once a motor is turning it doesn't stop instantly. How quickly it stops
    # depends on how fast it is moving. The return values below are from trial
    # and error with a NXT motor
    #
    # Return the number of milliseconds it will take to stop a motor.
    #
    def get_stop_delay(self, ticks, milliseconds):

        ticks_per_ms = float(ticks/milliseconds)
        #logger.debug('get_stop_delay ticks_per_ms %s' % ticks_per_ms)

        if ticks_per_ms >= 0.75:
            return 45

        elif ticks_per_ms >= 0.60:
            return 44

        elif ticks_per_ms >= 0.50:
            return 43

        elif ticks_per_ms >= 0.40:
            return 42

        elif ticks_per_ms >= 0.30:
            return 45

        elif ticks_per_ms >= 0.20:
            return 45

        elif ticks_per_ms >= 0.10:
            return 30

        return 0

    def rotate(self, power, degrees):
        self.power = abs(power)

        if degrees == 0:
            return

        # For running clockwise and anticlockwise
        if degrees > 0:
            self.speed = self.power
        else:
            self.speed = -1 * self.power

        self.brickpi.update_values()
        self.update_position()

        # Final value when the motor has to be stopped; One encoder value counts for 0.5 degrees
        self.target_position = self.position + (degrees * 2)

        logger.info('%s: Rotate with power %d, degrees %d, speed %d, move from %d/%d to %d/%d' % \
                    (self, self.power, degrees, self.speed,
                     self.position%720/2, self.position,
                     self.target_position%720/2, self.target_position))

        prev_time_ms = self.brickpi.current_time_ms()
        prev_position = self.position

        # Turn on the motor
        self.enabled = 1
        self.brickpi.update_values()

        # Go to sleep for the default amount of 100ms
        default_sleep_time_ms = float(100)
        sleep_error_ms = self.brickpi.sleep_error_ms
        time.sleep(float(default_sleep_time_ms - sleep_error_ms)/1000)

        # This lets you print the degree symbol
        degree_str =  u'\xb0'

        while True:

            # We've been asleep for (probably) 100ms, note the current time
            now_ms = self.brickpi.current_time_ms()

            # Ask BrickPi to update values for sensors/motors...this takes 10ms
            if not self.brickpi.update_values():
                logger.error('update_values returned False')
                break

            # Update the position for this motor
            self.update_position()

            ticks_to_go = abs(self.target_position - self.position)
            ticks_delta = abs(float(self.position - prev_position))

            if not ticks_delta:
                self.stop(False)
                logger.error('Not enough power to turn the motor')
                return

            time_delta = float(now_ms - prev_time_ms)
            ticks_per_ms = ticks_delta/time_delta
            ticks_to_go = abs(self.target_position - self.position)
            time_to_sleep = float(ticks_to_go/ticks_per_ms)

            '''
            logger.debug("%s: position %3d%s, %3d%s to go, moved %3d%s in the last %dms, will reach target in %dms" % \
                         (self,
                          (self.position%720)/2, degree_str,
                          ticks_to_go/2, degree_str,
                          ticks_delta%720/2, degree_str, time_delta,
                          time_to_sleep))
            '''

            # We are within 200ms of our target position.  Calculate how many ms
            # to sleep so that we can wake up, stop the motor and hopefully be
            # at the correct position.
            if time_to_sleep < 200:
                stop_delay = self.get_stop_delay(ticks_delta, time_delta)
                sleep_for_ms = float(int(time_to_sleep - stop_delay - sleep_error_ms))
                #logger.debug('%s: Final sleep for %sms' % (self, sleep_for_ms))
                if sleep_for_ms > 0:
                    time.sleep(sleep_for_ms/1000)
                self.stop(True)
                return

            # Sleep for 100ms
            else:
                time.sleep(float(default_sleep_time_ms - sleep_error_ms)/1000)
                prev_time_ms = now_ms
                prev_position = self.position


class BrickPi():

    def __init__(self):
        self.Address = [ 1, 2 ]
        self.ser = serial.Serial()
        self.ser.port='/dev/ttyAMA0'
        self.ser.baudrate = 500000

        # Not sure if this varies from Pi to Pi but on mine if you tell it to
        # sleep for 100ms it sleeps for 103ms or 104ms
        self.sleep_error_ms = 4

        self.motors = []
        for port in (PORT_A, PORT_B, PORT_C, PORT_D):
            self.motors.append(Motor(self, port))

        self.EncoderOffset    = [None] * 4
        self.Encoder          = [None] * 4
        self.Sensor           = [None] * 4
        self.SensorArray      = [ [None] * 4 for i in range(4) ]
        self.SensorType       = [0] * 4
        self.SensorSettings   = [ [None] * 8 for i in range(4) ]
        self.SensorI2CDevices = [None] * 4
        self.SensorI2CSpeed   = [None] * 4
        self.SensorI2CAddr    = [ [None] * 8 for i in range(4) ]
        self.SensorI2CWrite   = [ [None] * 8 for i in range(4) ]
        self.SensorI2CRead    = [ [None] * 8 for i in range(4) ]
        self.SensorI2COut     = [ [ [None] * 16 for i in range(8) ] for i in range(4) ]
        self.SensorI2CIn      = [ [ [None] * 16 for i in range(8) ] for i in range(4) ]
        self.Timeout = 0

        self.Array         = [0] * 256
        self.BytesReceived = None
        self.Bit_Offset    = 0
        self.Retried       = 0

        # BrickPiSetup
        if not self.ser.isOpen():
            self.ser.open()
        assert self.ser.isOpen(), "Serial failed to open"

        # Get the initial motor positions
        self.update_values()
        for motor in self.motors:
            motor.update_position()

    # BrickPiSetupSensors
    def SetupSensors(self):
        for i in range(2):
            self.Array = [0] * 256
            self.Bit_Offset = 0
            self.Array[BYTE_MSG_TYPE]      = MSG_TYPE_SENSOR_TYPE
            self.Array[BYTE_SENSOR_1_TYPE] = self.SensorType[PORT_1 + i*2]
            self.Array[BYTE_SENSOR_2_TYPE] = self.SensorType[PORT_2 + i*2]

            for ii in range(2):
                port = i*2 + ii

                if self.Array[BYTE_SENSOR_1_TYPE + ii] == TYPE_SENSOR_ULTRASONIC_CONT:
                    self.Array[BYTE_SENSOR_1_TYPE + ii]    = TYPE_SENSOR_I2C
                    self.SensorI2CSpeed[port]              = US_I2C_SPEED
                    self.SensorI2CDevices[port]            = 1
                    self.SensorSettings[port][US_I2C_IDX]  = BIT_I2C_MID | BIT_I2C_SAME
                    self.SensorI2CAddr[port][US_I2C_IDX]   = LEGO_US_I2C_ADDR
                    self.SensorI2CWrite[port][US_I2C_IDX]  = 1
                    self.SensorI2CRead[port][US_I2C_IDX]   = 1
                    self.SensorI2COut[port][US_I2C_IDX][0] = LEGO_US_I2C_DATA_REG

                if (self.Array[BYTE_SENSOR_1_TYPE + ii] == TYPE_SENSOR_I2C or
                    self.Array[BYTE_SENSOR_1_TYPE + ii] == TYPE_SENSOR_I2C_9V):

                    self.AddBits(3, 0, 8,self.SensorI2CSpeed[port])

                    if self.SensorI2CDevices[port] > 8:
                        self.SensorI2CDevices[port] = 8

                    if self.SensorI2CDevices[port] == 0:
                        self.SensorI2CDevices[port] = 1

                    self.AddBits(3, 0, 3, (self.SensorI2CDevices[port] - 1))

                    for device in range(self.SensorI2CDevices[port]):
                        self.AddBits(3, 0, 7, (self.SensorI2CAddr[port][device] >> 1))
                        self.AddBits(3, 0, 2, self.SensorSettings[port][device])

                        if(self.SensorSettings[port][device] & BIT_I2C_SAME):
                            self.AddBits(3, 0, 4, self.SensorI2CWrite[port][device])
                            self.AddBits(3, 0, 4, self.SensorI2CRead[port][device])

                            for out_byte in range(self.SensorI2CWrite[port][device]):
                                self.AddBits(3, 0, 8, self.SensorI2COut[port][device][out_byte])

            tx_bytes = (((self.Bit_Offset + 7) / 8) + 3) #eq to UART_TX_BYTES
            self.transmit(self.Address[i], tx_bytes , self.Array)
            (res, BytesReceived, InArray) = self.receive(0.500000)

            for i in range(len(InArray)):
                self.Array[i] = InArray[i]

        self.update_values()

    def current_time_ms(self):
        return int(round(time.time() * 1000))

    def GetBits(self, byte_offset, bit_offset, bits):
        result = 0
        i = bits
        while i:
            result *= 2
            result |= ((self.Array[(byte_offset + ((bit_offset + self.Bit_Offset + (i-1)) / 8))] >> ((bit_offset + self.Bit_Offset + (i-1)) % 8)) & 0x01)
            i -= 1
        self.Bit_Offset += bits
        return result

    def BitsNeeded(self, value):
        for i in range(32):
            if not value:
                return i
            value /= 2
        return 31

    def AddBits(self, byte_offset, bit_offset, bits, value):
        for i in range(bits):
            if value & 0x01:
                self.Array[(byte_offset + ((bit_offset + self.Bit_Offset + i)/ 8))] |= (0x01 << ((bit_offset + self.Bit_Offset + i) % 8));
            value /=2
        self.Bit_Offset += bits

    def transmit(self, dest, ByteCount, OutArray):
        tx_buffer = ''
        tx_buffer += chr(dest)
        tx_buffer += chr((dest+ByteCount+sum(OutArray[:ByteCount]))%256)
        tx_buffer += chr(ByteCount)

        for i in OutArray[:ByteCount]:
            tx_buffer += chr(i)

        self.ser.write(tx_buffer)

    def receive(self, timeout):
        rx_buffer = ''
        self.ser.timeout=0
        ot = time.time()

        while self.ser.inWaiting() <= 0:
            if time.time() - ot >= timeout :
                return (-2, 0, [])

        if not self.ser.isOpen():
            return (-1, 0, [])

        try:
            while self.ser.inWaiting():
                rx_buffer += ( self.ser.read(self.ser.inWaiting()) )
        except:
            return (-1, 0, [])

        RxBytes=len(rx_buffer)

        if RxBytes < 2 :
            return (-4, 0, [])

        if RxBytes < ord(rx_buffer[1])+2 :
            return (-6, 0, [])

        CheckSum = 0
        for i in rx_buffer[1:]:
            CheckSum += ord(i)

        InArray = []
        for i in rx_buffer[2:]:
            InArray.append(ord(i))

        # Checksum equals sum(InArray)+len(InArray)
        if (CheckSum % 256) != ord(rx_buffer[0]):
            return (-5, 0, [])

        InBytes = RxBytes - 2

        return (0, InBytes, InArray)

    def update_values(self, debug=False):
        if debug:
            logger.info('')
            logger.info('update_values start')
        ret = False
        i = 0

        while i < 2 :
            if debug:
                logger.info('update_values loop start')

            if not ret:
                Retried = 0
            # Retry Communication from here, if failed

            self.Array = [0] * 256
            self.Array[BYTE_MSG_TYPE] = MSG_TYPE_VALUES
            self.Bit_Offset = 0

            # Loop over ports 0 & 1 when 'i' is 0
            # Loop over ports 2 & 3 when 'i' is 1
            for ii in range(2):
                port = (i * 2) + ii

                if debug:
                    logger.info('update_values loop1, i %d, ii %d, port %d' % (i, ii, port))

                if self.EncoderOffset[port]:
                    Temp_Value = self.EncoderOffset[port]
                    self.AddBits(1, 0, 1, 1)
                    Temp_ENC_DIR = 0

                    if Temp_Value < 0 :
                        Temp_ENC_DIR = 1
                        Temp_Value *= -1

                    Temp_BitsNeeded = self.BitsNeeded(Temp_Value) + 1
                    self.AddBits(1, 0, 5, Temp_BitsNeeded)
                    Temp_Value *= 2
                    Temp_Value |= Temp_ENC_DIR
                    self.AddBits(1, 0, Temp_BitsNeeded, Temp_Value)

                else:
                    self.AddBits(1, 0, 1, 0)

            # Motors
            # Loop over ports 0 & 1 when 'i' is 0
            # Loop over ports 2 & 3 when 'i' is 1
            for ii in range(2):
                port = (i *2) + ii
                if debug:
                    logger.info('update_values loop2, i %d, ii %d, port %d' % (i, ii, port))
                motor = self.motors[port]
                speed = motor.speed
                direc = 0

                if speed < 0:
                    direc = 1
                    speed *= -1

                if speed > 255:
                    speed = 255

                self.AddBits(1, 0, 10, ((((speed & 0xFF) << 2) | (direc << 1) | (motor.enabled & 0x01)) & 0x3FF))

            # Sensors
            # Loop over ports 0 & 1 when 'i' is 0
            # Loop over ports 2 & 3 when 'i' is 1
            for ii in range(2):
                port =  (i * 2) + ii
                if debug:
                    logger.info('update_values loop3, i %d, ii %d, port %d' % (i, ii, port))

                if (self.SensorType[port] == TYPE_SENSOR_I2C or
                    self.SensorType[port] == TYPE_SENSOR_I2C_9V or
                    self.SensorType[port] == TYPE_SENSOR_ULTRASONIC_CONT):

                    for device in range(self.SensorI2CDevices[port]):
                        if not (self.SensorSettings[port][device] & BIT_I2C_SAME):
                            self.AddBits(1, 0, 4, self.SensorI2CWrite[port][device])
                            self.AddBits(1, 0, 4, self.SensorI2CRead[port][device])

                            for out_byte in range(self.SensorI2CWrite[port][device]):
                                self.AddBits(1, 0, 8, self.SensorI2COut[port][device][out_byte])
                        device += 1

            # eq to UART_TX_BYTES
            tx_bytes = (((self.Bit_Offset + 7) / 8 ) + 1)

            if debug:
                logger.info('update_values transmit begin %d bytes' % tx_bytes)

            self.transmit(self.Address[i], tx_bytes, self.Array)

            if debug:
                logger.info('update_values transmit end')

            # check timeout
            result, BytesReceived, InArray = self.receive(0.007500)
            for j in range(len(InArray)):
                self.Array[j] = InArray[j]

            if result != -2:
                self.EncoderOffset[(i * 2) + PORT_A] = 0
                self.EncoderOffset[(i * 2) + PORT_B] = 0

            if result or self.Array[BYTE_MSG_TYPE] != MSG_TYPE_VALUES:
                logger.error('receive Error :%s', result)

                if Retried < 2 :
                    ret = True
                    Retried += 1
                    continue
                else:
                    logger.error('Retry Failed')
                    return False

            ret = False
            self.Bit_Offset = 0

            Temp_BitsUsed = []
            Temp_BitsUsed.append(self.GetBits(1,0,5))
            Temp_BitsUsed.append(self.GetBits(1,0,5))

            for ii in range(2):
                Temp_EncoderVal = self.GetBits(1,0, Temp_BitsUsed[ii])

                if Temp_EncoderVal & 0x01 :
                    Temp_EncoderVal /= 2
                    self.Encoder[ii + i*2] = Temp_EncoderVal * (-1)
                else:
                    self.Encoder[ii + i*2] = Temp_EncoderVal / 2

            for ii in range(2):
                port = ii + (i * 2)
                if self.SensorType[port] == TYPE_SENSOR_TOUCH :
                    self.Sensor[port] = self.GetBits(1,0,1)

                elif self.SensorType[port] == TYPE_SENSOR_ULTRASONIC_SS :
                    self.Sensor[port] = GetBits(1,0,8)

                elif self.SensorType[port] == TYPE_SENSOR_COLOR_FULL:
                    self.Sensor[port] = GetBits(1,0,3)
                    self.SensorArray[port][INDEX_BLANK] = self.GetBits(1,0,10)
                    self.SensorArray[port][INDEX_RED]   = self.GetBits(1,0,10)
                    self.SensorArray[port][INDEX_GREEN] = self.GetBits(1,0,10)
                    self.SensorArray[port][INDEX_BLUE]  = self.GetBits(1,0,10)

                elif (self.SensorType[port] == TYPE_SENSOR_I2C or
                      self.SensorType[port] == TYPE_SENSOR_I2C_9V or
                      self.SensorType[port] == TYPE_SENSOR_ULTRASONIC_CONT):

                    self.Sensor[port] = GetBits(1,0, self.SensorI2CDevices[port])
                    for device in range(self.SensorI2CDevices[port]):
                        if (self.Sensor[port] & ( 0x01 << device)) :
                            for in_byte in range(self.SensorI2CRead[port][device]):
                                self.SensorI2CIn[port][device][in_byte] = GetBits(1,0,8)

                if self.SensorType[port] == TYPE_SENSOR_ULTRASONIC_CONT :
                    if(self.Sensor[port] & ( 0x01 << US_I2C_IDX)) :
                         self.Sensor[port] = self.SensorI2CIn[port][US_I2C_IDX][0]
                    else:
                        self.Sensor[port] = -1

                #For all the light, color and raw sensors
                else:
                    self.Sensor[ii + (i * 2)] = self.GetBits(1,0,10)

            i += 1
            if debug:
                logger.info('update_values i = %d' % i)

        if debug:
            logger.info('update_values end')
        return True

