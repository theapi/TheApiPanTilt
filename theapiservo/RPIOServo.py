#!/usr/bin/python

import RPIO
import RPIO.PWM

from theapiservo.BaseServo import BaseServo

class RPIOServo(BaseServo):

    def addChannelPulse(self, dma_channel, gpio, start, width):
        RPIO.PWM.add_channel_pulse( dma_channel, gpio, start, width )

