# drivers

import imp

class Drivers:

    def getDriver(self, args, frequency, pulse_incr_us):

        if ('rpio' == args.driver):
            try:
                imp.find_module('RPIO')
                from theapipantilt.drivers.rpiodriver import RPIOServoControl as ServoControl
            except ImportError:
                from theapipantilt.drivers.dummydriver import DummyServoControl as ServoControl

            return ServoControl(frequency, pulse_incr_us)

        elif ('cube' == args.driver):
            try:
                from theapipantilt.drivers.cube import CubeServoControl as ServoControl
            except ImportError:
                from theapipantilt.drivers.dummydriver import DummyServoControl as ServoControl

            return ServoControl(frequency, pulse_incr_us)

        else:
            from theapipantilt.drivers.dummydriver import DummyServoControl as ServoControl
            return ServoControl(frequency, pulse_incr_us)

