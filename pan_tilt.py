# -*- coding: utf-8 -*-

from picam.client import JoystickClient
from picam.dummyservo import ServoControl, Servo


PWM_FREQUENCY = 50    # Hz
PWM_PULSE_INCREMENT_US = 5
PAN_PWM_PIN = 23
TILT_PWM_PIN = 24

servoControl = ServoControl(PWM_FREQUENCY, PWM_PULSE_INCREMENT_US)
# Create Servo instances to control the servos
panServo = servoControl.getServo( PAN_PWM_PIN,
    minAnglePulseWidthPair=( 50.0, 2100 ),
    midAnglePulseWidthPair=( 90.0, 1300 ),
    maxAnglePulseWidthPair=( 130.0, 800.0 ) )

tiltServo = servoControl.getServo( TILT_PWM_PIN,
    minAnglePulseWidthPair=( 45.0, 2100 ),
    midAnglePulseWidthPair=( 90.0, 1800 ),
    maxAnglePulseWidthPair=( 135.0, 900.0 ) )

try:
    ws = JoystickClient('ws://localhost:9000/ws', protocols=['http-only', 'chat'])
    ws.addPanServo(panServo)
    ws.addTiltServo(tiltServo)
    ws.connect()
    ws.run_forever()
except KeyboardInterrupt:
    ws.close()
