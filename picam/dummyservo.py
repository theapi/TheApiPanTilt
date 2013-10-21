#!/usr/bin/python


class ServoControl:

    def __init__(self, frequency, pulse_incr_us):

        self.gpioMode = RPIO.BCM
        self.channel = 0
        self.frequency = frequency
        self.pulse_incr_us = pulse_incr_us

        self.subcycle_time_us = 1000/frequency * 1000

        # Setup RPIO, and prepare for PWM signals
        #RPIO.setmode( self.gpioMode )
        #RPIO.PWM.set_loglevel(RPIO.PWM.LOG_LEVEL_ERRORS)
        #RPIO.PWM.setup( pulse_incr_us = self.pulse_incr_us )
        #RPIO.PWM.init_channel( self.channel, self.subcycle_time_us )

    def getServo(self, pin, minAnglePulseWidthPair, midAnglePulseWidthPair, maxAnglePulseWidthPair):
        return Servo( self.channel, pin, minAnglePulseWidthPair, midAnglePulseWidthPair, maxAnglePulseWidthPair )

class Servo:

    #---------------------------------------------------------------------------
    def __init__( self, channel, pwmPin, minAnglePulseWidthPair,
        midAnglePulseWidthPair, maxAnglePulseWidthPair ):

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

        self.absoluteMinPulseWidthUs = 500 #todo setter
        self.absoluteMaxPulseWidthUs = 2500 #todo setter

        self.lastPulseWidthSet = None
        self.lastPulseIncrement = 0
        self.lastJoystickInput = 0

    #---------------------------------------------------------------------------
    def setPulseWidth( self, pulseWidth ):

        # Constrain the pulse width
        if pulseWidth < self.absoluteMinPulseWidthUs:
            pulseWidth = self.absoluteMinPulseWidthUs
        if pulseWidth > self.absoluteMaxPulseWidthUs:
            pulseWidth = self.absoluteMaxPulseWidthUs

        # Ensure that the pulse width is an integer multiple of the smallest
        # possible pulse increment
        #pulseIncrementUS = RPIO.PWM.get_pulse_incr_us()
        pulseIncrementUS = PWM_PULSE_INCREMENT_US
        numPulsesNeeded = int( pulseWidth/pulseIncrementUS )
        pulseWidth = numPulsesNeeded * pulseIncrementUS

        if pulseWidth != self.lastPulseWidthSet:

            RPIO.PWM.add_channel_pulse( self.channel, self.pwmPin, 0, numPulsesNeeded )
            self.lastPulseWidthSet = pulseWidth

    #---------------------------------------------------------------------------
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

    #---------------------------------------------------------------------------
    def joystickInput( self, px ):

        # Do not map pixel to increment.
        # Just whether movement required, and what speed.
        # Joystick off center by small amount = small incremental move.
        # Joystick off center by large amount = large incremental move.

        step = 10

        pulseIncrement = 0

        if px > 0:
            pulseIncrement = step
            if px > 50:
                pulseIncrement = step * 3

        if px < 0:
            pulseIncrement = step * -1
            if px < -50:
                pulseIncrement = step * 3 * -1

        self.lastJoystickInput = pulseIncrement
        #print str(pulseIncrement)


    #---------------------------------------------------------------------------
    def getLastJoystickInput( self ):
        return self.lastJoystickInput;



