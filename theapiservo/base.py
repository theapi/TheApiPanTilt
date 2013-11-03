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



class BaseServo:

    def __init__( self, channel, pwmPin, minAnglePulseWidthPair,
        midAnglePulseWidthPair, maxAnglePulseWidthPair, pulsIncrUs ):

        # Check that the given angles are valid
        assert( minAnglePulseWidthPair[ 0 ] >= 0 )
        assert( midAnglePulseWidthPair[ 0 ] > minAnglePulseWidthPair[ 0 ] )
        assert( midAnglePulseWidthPair[ 0 ] < maxAnglePulseWidthPair[ 0 ] )
        assert( maxAnglePulseWidthPair[ 0 ] <= 180 )

        self.pwmPin = pwmPin
        self.channel = channel
        self.minAnglePulseWidthPair = minAnglePulseWidthPair
        self.midAnglePulseWidthPair = midAnglePulseWidthPair
        self.maxAnglePulseWidthPair = maxAnglePulseWidthPair
        self.pulsIncrUs = pulsIncrUs

        self.absoluteMinPulseWidthUs = 500 #todo setter
        self.absoluteMaxPulseWidthUs = 2500 #todo setter

        self.lastPulseWidthSet = None
        self.lastPulseIncrement = 0
        self.lastJoystickInput = 0

    def getPulseIncrementUS( self ):
        return self.pulsIncrUs

    def setPulseWidth( self, pulseWidth ):

        # Constrain the pulse width
        if pulseWidth < self.absoluteMinPulseWidthUs:
            pulseWidth = self.absoluteMinPulseWidthUs
        if pulseWidth > self.absoluteMaxPulseWidthUs:
            pulseWidth = self.absoluteMaxPulseWidthUs

        # Ensure that the pulse width is an integer multiple of the smallest
        # possible pulse increment
        pulseIncrementUS = self.getPulseIncrementUS()
        numPulsesNeeded = int( pulseWidth/pulseIncrementUS )
        pulseWidth = numPulsesNeeded * pulseIncrementUS

        if pulseWidth != self.lastPulseWidthSet:
            self.addChannelPulse( self.channel, self.pwmPin, 0, numPulsesNeeded )
            self.lastPulseWidthSet = pulseWidth

    def addChannelPulse(self, dma_channel, gpio, start, width):
        #RPIO.PWM.add_channel_pulse( dma_channel, gpio, start, width )
        pass

    def movePulseIncrement( self, pulseIncrement ):

        self.lastPulseIncrement = pulseIncrement

        if self.lastPulseWidthSet is None:
            command = self.midAnglePulseWidthPair[ 1 ] + pulseIncrement
        else:
            command = self.lastPulseWidthSet + pulseIncrement

        # Stop it going too far for this servo's settings.
        if command < self.maxAnglePulseWidthPair[ 1 ]:
            command = self.maxAnglePulseWidthPair[ 1 ]
        elif command >self.minAnglePulseWidthPair[ 1 ]:
            command = self.minAnglePulseWidthPair[ 1 ]

        print 'setPulseWidth: ' + str(command)
        self.setPulseWidth( command )

