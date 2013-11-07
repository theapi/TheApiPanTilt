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
        self.panServo.move(self.vectorX)
        self.tiltServo.move(self.vectorY)


    def setVector(self, m):
        vector = m.split(',')
        #print m
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

        self.currentPosition = 0

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

    def move(self, destination):
         # Jump straight there.
         self.currentPosition = destination
         #self.movePulseIncrement(destination)
         command = self.midPulseWidth + (destination * 5)
         self.setPulseWidth(command)
         
         return destination

