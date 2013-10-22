# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_all()

import math
import time
import gevent
from ws4py.client.geventclient import WebSocketClient

from picam.dummyservo import ServoControl, Servo

PWM_FREQUENCY = 50    # Hz
PWM_PULSE_INCREMENT_US = 5
PAN_PWM_PIN = 23
TILT_PWM_PIN = 24



if __name__ == '__main__':

    servoControl = ServoControl(PWM_FREQUENCY, PWM_PULSE_INCREMENT_US)

    # Create Servo instances to control the servos
    panServo = servoControl.getPanServo( PAN_PWM_PIN,
        minAnglePulseWidthPair=( 50.0, 2100 ),
        midAnglePulseWidthPair=( 90.0, 1300 ),
        maxAnglePulseWidthPair=( 130.0, 800.0 ) )

    tiltServo = servoControl.getTiltServo( TILT_PWM_PIN,
        minAnglePulseWidthPair=( 45.0, 2100 ),
        midAnglePulseWidthPair=( 90.0, 1800 ),
        maxAnglePulseWidthPair=( 135.0, 900.0 ) )


    ws = WebSocketClient('ws://localhost:9001/ws', protocols=['http-only', 'chat'])
    ws.connect()

    ws.send("Hello world")
    print((ws.receive(),))

    ws.send("Hello world again")
    print((ws.receive(),))

    def incoming():
        while True:
            m = ws.receive()
            if m is not None:
                m = str(m)
                print "WS: " + m
                servoControl.setVector(m)

                if len(m) == 35:
                    ws.close()
                    break
            else:
                break
        print(("Connection closed!",))

    def joystick():
        while True:
            time.sleep(0.1)
            # Move if joystick is not centered
            #x = panServo.getLastJoystickInput()
            #y = tiltServo.getLastJoystickInput()

            servoControl.move()

            #if (x != 0):
            #    panServo.movePulseIncrement( x )
            #if (y != 0):
            #    tiltServo.movePulseIncrement( y )


    greenlets = [
        gevent.spawn(incoming),
        gevent.spawn(joystick),
    ]
    gevent.joinall(greenlets)
