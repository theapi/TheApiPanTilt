#!/usr/bin/python


from theapiservo.base import *

class DummyServoControl(BaseServoControl):

    def __init__(self, frequency, pulse_incr_us):

        BaseServoControl.__init__(self, DummyServo, frequency, pulse_incr_us)


class DummyServo(BaseServo):

    def addChannelPulse(self, dma_channel, gpio, start, width):
        pass
