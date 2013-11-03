#!/usr/bin/python


from theapiservo.BaseServoControl import BaseServoControl
from theapiservo.DummyServo import DummyServo as Servo

class DummyServoControl(BaseServoControl):

    def __init__(self, frequency, pulse_incr_us):

        BaseServoControl.__init__(self, Servo, frequency, pulse_incr_us)
