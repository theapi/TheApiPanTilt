#!/usr/bin/python

import RPIO
import RPIO.PWM

from Servo import Servo

class ServoControl:

    def __init__(self, frequency, pulse_incr_us):

        self.gpioMode = RPIO.BCM
        self.channel = 0
        self.frequency = frequency
        self.pulse_incr_us = pulse_incr_us

        self.subcycle_time_us = 1000/frequency * 1000

        # Setup RPIO, and prepare for PWM signals
        RPIO.setmode( self.gpioMode )
        RPIO.PWM.set_loglevel(RPIO.PWM.LOG_LEVEL_ERRORS)
        RPIO.PWM.setup( pulse_incr_us = self.pulse_incr_us )
        RPIO.PWM.init_channel( self.channel, self.subcycle_time_us )

    def getServo(self, pin, minAnglePulseWidthPair, midAnglePulseWidthPair, maxAnglePulseWidthPair):
        return Servo( self.channel, pin, minAnglePulseWidthPair, midAnglePulseWidthPair, maxAnglePulseWidthPair )


