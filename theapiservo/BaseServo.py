


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

