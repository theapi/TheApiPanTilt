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
        self.step = 5

    def initPanServo(self, pin, minWidth, midWidth, maxWidth):
        self.panServo = self.Servo( self.channel, pin, minWidth, midWidth, maxWidth, self.pulse_incr_us )

    def initTiltServo(self, pin, minWidth, midWidth, maxWidth):
        self.tiltServo = self.Servo( self.channel, pin, minWidth, midWidth, maxWidth, self.pulse_incr_us )

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

        pulseIncrement = 0

        if px > 0:
            pulseIncrement = self.step
            if px > 25:
                pulseIncrement = self.step * 2
                if px > 50:
                    pulseIncrement = self.step * 10

        if px < 0:
            pulseIncrement = self.step * -1
            if px < -25:
                pulseIncrement = self.step * 2 * -1
                if px < -50:
                    pulseIncrement = self.step * 10 * -1

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



class BaseServo:

    def __init__( self, channel, pwmPin, minPulseWidth,
        midPulseWidth, maxPulseWidth, pulsIncrUs ):

        # Check that the pulse widths are valid
        assert( midPulseWidth > minPulseWidth )
        assert( midPulseWidth < maxPulseWidth )

        self.pwmPin = pwmPin
        self.channel = channel
        self.minPulseWidth = minPulseWidth
        self.midPulseWidth = midPulseWidth
        self.maxPulseWidth = maxPulseWidth
        self.pulsIncrUs = pulsIncrUs

        self.lastPulseWidthSet = None
        self.lastPulseIncrement = 0
        self.lastJoystickInput = 0

        # Center the servo
        self.setPulseWidth( self.midPulseWidth )

    def getPulseIncrementUS( self ):
        return self.pulsIncrUs

    def setPulseWidth( self, pulseWidth ):

        # Constrain the pulse width
        if pulseWidth < self.minPulseWidth:
            pulseWidth = self.minPulseWidth
        if pulseWidth > self.maxPulseWidth:
            pulseWidth = self.maxPulseWidth

        # Ensure that the pulse width is an integer multiple of the smallest
        # possible pulse increment
        pulseIncrementUS = self.getPulseIncrementUS()
        numPulsesNeeded = int( pulseWidth/pulseIncrementUS )
        pulseWidth = numPulsesNeeded * pulseIncrementUS

        if pulseWidth != self.lastPulseWidthSet:
            self.addChannelPulse( self.channel, self.pwmPin, 0, numPulsesNeeded )
            self.lastPulseWidthSet = pulseWidth
            print 'pin: ' + str(self.pwmPin) + ' -> ' + str(pulseWidth)
            return True

        return False

    def addChannelPulse(self, dma_channel, gpio, start, width):
        #RPIO.PWM.add_channel_pulse( dma_channel, gpio, start, width )
        pass

    def movePulseIncrement( self, pulseIncrement ):
        self.lastPulseIncrement = pulseIncrement
        command = self.lastPulseWidthSet + pulseIncrement
        return self.setPulseWidth( command )


