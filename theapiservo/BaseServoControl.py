#!/usr/bin/python


class BaseServoControl:

    def __init__(self, servoclass, frequency, pulse_incr_us):
        self.Servo = servoclass
        self.channel = 0
        self.frequency = frequency
        self.pulse_incr_us = pulse_incr_us

        self.subcycle_time_us = 1000/frequency * 1000

        self.panServo = None
        self.tiltServo = None
        self.vectorX = 0
        self.vectorY = 0
        self.slack = 1
        self.invertPan = False
        self.invertTilt = False

    def getPanServo(self, pin, minAnglePulseWidthPair, midAnglePulseWidthPair, maxAnglePulseWidthPair):
        self.panServo = self.Servo( self.channel, pin, minAnglePulseWidthPair, midAnglePulseWidthPair, maxAnglePulseWidthPair, self.pulse_incr_us )
        return self.panServo

    def getTiltServo(self, pin, minAnglePulseWidthPair, midAnglePulseWidthPair, maxAnglePulseWidthPair):
        self.tiltServo = self.Servo( self.channel, pin, minAnglePulseWidthPair, midAnglePulseWidthPair, maxAnglePulseWidthPair, self.pulse_incr_us )
        return self.tiltServo

    def setInvertPan(self, b):
        if (b):
            self.invertPan = True

    def setInvertTilt(self, b):
        if (b):
            self.invertTilt = True

    def move(self):
        # Allow some slack with up & down
        # So you don't need to be exactly 0 to move in one axis.

        if ( (self.slack == 0) or (self.vectorX < -self.slack or self.vectorX > self.slack) ):
            incrementX = self.getPulseIncrement(self.vectorX)
            if (incrementX != 0):
                self.panServo.movePulseIncrement( incrementX )

        if ( (self.slack == 0) or (self.vectorY < -self.slack or self.vectorY > self.slack) ):
            incrementY = self.getPulseIncrement(self.vectorY)
            if (incrementY != 0):
                self.tiltServo.movePulseIncrement( incrementY )

    def getPulseIncrement(self, px):
        # Do not map pixel to increment.
        # Just whether movement required, and what speed.
        # Joystick off center by small amount = small incremental move.
        # Joystick off center by large amount = large incremental move.

        step = 5
        pulseIncrement = 0

        if px > 0:
            pulseIncrement = step
            if px > 25:
                pulseIncrement = step * 2
                if px > 50:
                    pulseIncrement = step * 10

        if px < 0:
            pulseIncrement = step * -1
            if px < -25:
                pulseIncrement = step * 2 * -1
                if px < -50:
                    pulseIncrement = step * 10 * -1

        return pulseIncrement

    def setVector(self, m):
        vector = m.split(',')
        try:
            self.vectorX = int( vector[0].strip() )
            self.vectorY = int( vector[1].strip() )

            if (self.invertPan):
                self.vectorX = self.vectorX * -1

            if (self.invertTilt):
                self.vectorY = self.vectorY * -1

            #print math.degrees(math.atan2(self.vectorX, self.vectorY))
        except ValueError:
            # not a vector
            return

