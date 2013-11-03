#!/usr/bin/python

from theapiservo.BaseServo import BaseServo

class DummyServo(BaseServo):

    def addChannelPulse(self, dma_channel, gpio, start, width):
        pass

