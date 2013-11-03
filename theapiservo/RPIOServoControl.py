#!/usr/bin/python

import RPIO
import RPIO.PWM

from theapiservo.BaseServoControl import BaseServoControl
from theapiservo.RPIOServo import RPIOServo as Servo

class RPIOServoControl(BaseServoControl):

    def __init__(self, frequency, pulse_incr_us):

        BaseServoControl.__init__(self, frequency, pulse_incr_us)

        self.gpioMode = RPIO.BCM

        # Setup RPIO, and prepare for PWM signals
        RPIO.setmode( self.gpioMode )
        RPIO.PWM.set_loglevel(RPIO.PWM.LOG_LEVEL_ERRORS)
        RPIO.PWM.setup( pulse_incr_us = self.pulse_incr_us )
        RPIO.PWM.init_channel( self.channel, self.subcycle_time_us )


